"""
API роутер для лидов (версия 2 с сервисным слоем)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.db import get_db
from app.services.lead_service import LeadService
from app.schemas.leads import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadListResponse,
    LeadFilter,
    LeadStatistics
)
from app.core.dependencies import get_current_active_user, get_pagination_params, get_search_params
from app.models.user import User

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("/", response_model=LeadListResponse)
async def get_leads(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    source: Optional[str] = Query(None, description="Фильтр по источнику"),
    assigned_to: Optional[int] = Query(None, description="Фильтр по назначенному пользователю"),
    search: Optional[str] = Query(None, description="Поиск по тексту"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка лидов с фильтрацией и пагинацией
    """
    lead_service = LeadService(db)
    
    # Создаем фильтр
    filters = LeadFilter(
        status=status,
        source=source,
        assigned_to=assigned_to,
        search=search
    )
    
    # Вычисляем offset
    skip = (page - 1) * per_page
    
    # Получаем лиды
    leads = lead_service.get_leads(skip=skip, limit=per_page, filters=filters)
    
    # Получаем общее количество для пагинации
    total_leads = len(lead_service.get_leads(filters=filters))  # Упрощенно, в реальности нужен отдельный метод
    
    total_pages = (total_leads + per_page - 1) // per_page
    
    return LeadListResponse(
        leads=leads,
        total=total_leads,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового лида
    """
    lead_service = LeadService(db)
    lead = lead_service.create_lead(lead_data, user_id=current_user.id)
    return lead


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение лида по ID
    """
    lead_service = LeadService(db)
    lead = lead_service.get_lead_by_id(lead_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Лид не найден"
        )
    
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновление лида
    """
    lead_service = LeadService(db)
    lead = lead_service.update_lead(lead_id, lead_data)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Удаление лида
    """
    lead_service = LeadService(db)
    lead_service.delete_lead(lead_id)


@router.post("/{lead_id}/assign")
async def assign_lead(
    lead_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Назначение лида пользователю
    """
    lead_service = LeadService(db)
    lead = lead_service.assign_lead(lead_id, user_id)
    return {"message": "Лид успешно назначен", "lead": lead}


@router.post("/{lead_id}/status")
async def change_lead_status(
    lead_id: int,
    new_status: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Изменение статуса лида
    """
    lead_service = LeadService(db)
    lead = lead_service.change_lead_status(lead_id, new_status)
    return {"message": "Статус лида изменен", "lead": lead}


@router.get("/search", response_model=List[LeadResponse])
async def search_leads(
    q: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(20, ge=1, le=100, description="Максимальное количество результатов"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Поиск лидов по тексту
    """
    lead_service = LeadService(db)
    leads = lead_service.search_leads(q, limit=limit)
    return leads


@router.get("/my/", response_model=List[LeadResponse])
async def get_my_leads(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение лидов, назначенных текущему пользователю
    """
    lead_service = LeadService(db)
    skip = (page - 1) * per_page
    leads = lead_service.get_leads_by_user(current_user.id, skip=skip, limit=per_page)
    return leads


@router.get("/statistics", response_model=LeadStatistics)
async def get_lead_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение статистики по лидам
    """
    lead_service = LeadService(db)
    statistics = lead_service.get_lead_statistics(user_id=current_user.id)
    return statistics


@router.get("/statistics/all", response_model=LeadStatistics)
async def get_all_lead_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение общей статистики по лидам (для администраторов)
    """
    lead_service = LeadService(db)
    statistics = lead_service.get_lead_statistics()  # Без user_id для общей статистики
    return statistics
