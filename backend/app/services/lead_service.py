"""
Сервис для работы с лидами
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, desc, asc

from app.models.lead import Lead
from app.schemas.leads import LeadCreate, LeadUpdate, LeadFilter, LeadStatistics
from app.core.exceptions import (
    LeadNotFoundError,
    LeadAlreadyExistsError,
    ValidationError,
    DatabaseError
)


class LeadService:
    """Сервис для работы с лидами"""

    def __init__(self, db: Session):
        self.db = db

    def get_lead_by_id(self, lead_id: int) -> Optional[Lead]:
        """Получение лида по ID"""
        return self.db.query(Lead).filter(Lead.id == lead_id).first()

    def get_lead_by_email(self, email: str) -> Optional[Lead]:
        """Получение лида по email"""
        return self.db.query(Lead).filter(Lead.email == email).first()

    def get_leads(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[LeadFilter] = None
    ) -> List[Lead]:
        """Получение списка лидов с фильтрацией"""
        query = self.db.query(Lead)

        if filters:
            # Фильтр по статусу
            if filters.status:
                query = query.filter(Lead.status == filters.status)

            # Фильтр по источнику
            if filters.source:
                query = query.filter(Lead.source == filters.source)

            # Фильтр по назначенному пользователю
            if filters.assigned_to:
                query = query.filter(Lead.assigned_to == filters.assigned_to)

            # Фильтр по дате создания
            if filters.created_after:
                query = query.filter(Lead.created_at >= filters.created_after)

            if filters.created_before:
                query = query.filter(Lead.created_at <= filters.created_before)

            # Поиск по тексту
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Lead.first_name.ilike(search_term),
                        Lead.last_name.ilike(search_term),
                        Lead.email.ilike(search_term),
                        Lead.company.ilike(search_term),
                        Lead.notes.ilike(search_term)
                    )
                )

        # Сортировка по дате создания (новые сначала)
        query = query.order_by(desc(Lead.created_at))

        return query.offset(skip).limit(limit).all()

    def create_lead(self, lead_data: LeadCreate, user_id: Optional[int] = None) -> Lead:
        """Создание нового лида"""
        # Проверяем, существует ли лид с таким email
        existing_lead = self.get_lead_by_email(lead_data.email)
        if existing_lead:
            raise LeadAlreadyExistsError(f"Лид с email {lead_data.email} уже существует")

        # Создаем нового лида
        db_lead = Lead(
            first_name=lead_data.first_name,
            last_name=lead_data.last_name,
            email=lead_data.email,
            phone=lead_data.phone,
            company=lead_data.company,
            position=lead_data.position,
            source=lead_data.source,
            status=lead_data.status,
            notes=lead_data.notes,
            budget=lead_data.budget,
            timeline=lead_data.timeline,
            assigned_to=user_id
        )

        try:
            self.db.add(db_lead)
            self.db.commit()
            self.db.refresh(db_lead)
            return db_lead
        except IntegrityError:
            self.db.rollback()
            raise LeadAlreadyExistsError(f"Лид с email {lead_data.email} уже существует")

    def update_lead(self, lead_id: int, lead_data: LeadUpdate) -> Lead:
        """Обновление лида"""
        lead = self.get_lead_by_id(lead_id)
        if not lead:
            raise LeadNotFoundError(f"Лид с ID {lead_id} не найден")

        # Обновляем только переданные поля
        update_data = lead_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(lead, field, value)

        lead.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(lead)
            return lead
        except IntegrityError:
            self.db.rollback()
            raise LeadAlreadyExistsError("Лид с таким email уже существует")

    def delete_lead(self, lead_id: int) -> bool:
        """Удаление лида"""
        lead = self.get_lead_by_id(lead_id)
        if not lead:
            raise LeadNotFoundError(f"Лид с ID {lead_id} не найден")

        self.db.delete(lead)
        self.db.commit()
        return True

    def assign_lead(self, lead_id: int, user_id: int) -> Lead:
        """Назначение лида пользователю"""
        lead = self.get_lead_by_id(lead_id)
        if not lead:
            raise LeadNotFoundError(f"Лид с ID {lead_id} не найден")

        lead.assigned_to = user_id
        lead.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(lead)
        return lead

    def change_lead_status(self, lead_id: int, new_status: str) -> Lead:
        """Изменение статуса лида"""
        lead = self.get_lead_by_id(lead_id)
        if not lead:
            raise LeadNotFoundError(f"Лид с ID {lead_id} не найден")

        lead.status = new_status
        lead.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(lead)
        return lead

    def get_lead_statistics(self, user_id: Optional[int] = None) -> LeadStatistics:
        """Получение статистики по лидам"""
        query = self.db.query(Lead)

        if user_id:
            query = query.filter(Lead.assigned_to == user_id)

        total_leads = query.count()
        new_leads = query.filter(Lead.status == "new").count()
        contacted_leads = query.filter(Lead.status == "contacted").count()
        qualified_leads = query.filter(Lead.status == "qualified").count()

        # Конверсия (qualified / total)
        conversion_rate = (qualified_leads / total_leads * 100) if total_leads > 0 else 0

        # Статистика по источникам
        conversion_by_source = {}
        sources = self.db.query(Lead.source).distinct().all()
        for source in sources:
            source_count = query.filter(Lead.source == source[0]).count()
            conversion_by_source[source[0]] = source_count

        # Статистика по статусам
        conversion_by_status = {}
        statuses = self.db.query(Lead.status).distinct().all()
        for status in statuses:
            status_count = query.filter(Lead.status == status[0]).count()
            conversion_by_status[status[0]] = status_count

        return LeadStatistics(
            total_leads=total_leads,
            new_leads=new_leads,
            contacted_leads=contacted_leads,
            qualified_leads=qualified_leads,
            conversion_rate=conversion_rate,
            conversion_by_source=conversion_by_source,
            conversion_by_status=conversion_by_status
        )

    def get_leads_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Lead]:
        """Получение лидов, назначенных пользователю"""
        return (
            self.db.query(Lead)
            .filter(Lead.assigned_to == user_id)
            .order_by(desc(Lead.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_leads(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Lead]:
        """Поиск лидов по тексту"""
        search_pattern = f"%{search_term}%"
        return (
            self.db.query(Lead)
            .filter(
                or_(
                    Lead.first_name.ilike(search_pattern),
                    Lead.last_name.ilike(search_pattern),
                    Lead.email.ilike(search_pattern),
                    Lead.company.ilike(search_pattern),
                    Lead.notes.ilike(search_pattern)
                )
            )
            .order_by(desc(Lead.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
