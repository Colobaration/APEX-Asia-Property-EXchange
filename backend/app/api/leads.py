from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.integrations.amo.client import AmoCRMClient
from app.core.logging import logger
import re

router = APIRouter()

class LeadCreate(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None
    property_type: Optional[str] = None
    budget: Optional[float] = None
    notes: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Имя должно содержать минимум 2 символа')
        if len(v) > 100:
            raise ValueError('Имя не может быть длиннее 100 символов')
        return v.strip()

    @validator('phone')
    def validate_phone(cls, v):
        # Удаляем все нецифровые символы
        phone_clean = re.sub(r'\D', '', v)
        if len(phone_clean) < 10 or len(phone_clean) > 15:
            raise ValueError('Некорректный формат телефона')
        return phone_clean

    @validator('budget')
    def validate_budget(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Бюджет должен быть положительным числом')
        return v

    @validator('notes')
    def validate_notes(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Примечания не могут быть длиннее 1000 символов')
        return v

class LeadResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str]
    amocrm_contact_id: Optional[int]
    amocrm_lead_id: Optional[int]
    status: str
    created_at: str

@router.post("/", response_model=LeadResponse)
async def create_lead(lead_data: LeadCreate, db: Session = Depends(get_db)):
    """
    Создание нового лида с автоматической интеграцией в amoCRM
    """
    try:
        # Создаем клиент amoCRM
        amo_client = AmoCRMClient()
        
        # Проверяем подключение к amoCRM
        if not await amo_client.test_connection():
            raise HTTPException(status_code=500, detail="amoCRM connection failed")
        
        # Создаем или находим контакт в amoCRM
        contact = await amo_client.find_or_create_contact(
            name=lead_data.name,
            phone=lead_data.phone,
            email=lead_data.email
        )
        
        # Подготавливаем UTM данные
        utm_data = {}
        if lead_data.utm_source:
            utm_data["utm_source"] = lead_data.utm_source
        if lead_data.utm_medium:
            utm_data["utm_medium"] = lead_data.utm_medium
        if lead_data.utm_campaign:
            utm_data["utm_campaign"] = lead_data.utm_campaign
        if lead_data.utm_content:
            utm_data["utm_content"] = lead_data.utm_content
        if lead_data.utm_term:
            utm_data["utm_term"] = lead_data.utm_term
        
        # Создаем сделку в amoCRM
        lead_name = f"Лид: {lead_data.name}"
        if lead_data.property_type:
            lead_name += f" - {lead_data.property_type}"
        
        amo_lead = await amo_client.create_lead(
            contact_id=contact["id"],
            name=lead_name,
            utm_data=utm_data
        )
        
        # Добавляем теги
        if lead_data.property_type:
            await amo_client.add_tag_to_lead(amo_lead["id"], lead_data.property_type)
        
        if lead_data.budget:
            await amo_client.add_tag_to_lead(amo_lead["id"], f"Бюджет: {lead_data.budget}")
        
        # Сохраняем в локальную БД
        from app.models.lead import Lead
        from datetime import datetime
        
        db_lead = Lead(
            name=lead_data.name,
            phone=lead_data.phone,
            email=lead_data.email,
            amocrm_contact_id=contact["id"],
            amocrm_lead_id=amo_lead["id"],
            utm_source=lead_data.utm_source,
            utm_medium=lead_data.utm_medium,
            utm_campaign=lead_data.utm_campaign,
            utm_content=lead_data.utm_content,
            utm_term=lead_data.utm_term,
            property_type=lead_data.property_type,
            budget=lead_data.budget,
            notes=lead_data.notes,
            status="new",
            created_at=datetime.utcnow()
        )
        
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        
        logger.info(f"Lead created successfully: {db_lead.id} -> amoCRM: {amo_lead['id']}")
        
        return LeadResponse(
            id=db_lead.id,
            name=db_lead.name,
            phone=db_lead.phone,
            email=db_lead.email,
            amocrm_contact_id=db_lead.amocrm_contact_id,
            amocrm_lead_id=db_lead.amocrm_lead_id,
            status=db_lead.status,
            created_at=db_lead.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error creating lead: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {str(e)}")

@router.get("/", response_model=list[LeadResponse])
async def get_leads(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получение списка лидов с фильтрацией
    """
    try:
        from app.models.lead import Lead
        
        query = db.query(Lead)
        
        if status:
            query = query.filter(Lead.status == status)
        
        leads = query.offset(skip).limit(limit).all()
        
        return [
            LeadResponse(
                id=lead.id,
                name=lead.name,
                phone=lead.phone,
                email=lead.email,
                amocrm_contact_id=lead.amocrm_contact_id,
                amocrm_lead_id=lead.amocrm_lead_id,
                status=lead.status,
                created_at=lead.created_at.isoformat()
            )
            for lead in leads
        ]
        
    except Exception as e:
        logger.error(f"Error getting leads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get leads: {str(e)}")

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Получение информации о конкретном лиде
    """
    try:
        from app.models.lead import Lead
        
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return LeadResponse(
            id=lead.id,
            name=lead.name,
            phone=lead.phone,
            email=lead.email,
            amocrm_contact_id=lead.amocrm_contact_id,
            amocrm_lead_id=lead.amocrm_lead_id,
            status=lead.status,
            created_at=lead.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get lead: {str(e)}")

@router.put("/{lead_id}/status")
async def update_lead_status(
    lead_id: int, 
    status: str, 
    db: Session = Depends(get_db)
):
    """
    Обновление статуса лида с синхронизацией в amoCRM
    """
    try:
        from app.models.lead import Lead
        
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Обновляем статус в локальной БД
        lead.status = status
        db.commit()
        
        # Синхронизируем с amoCRM если есть ID сделки
        if lead.amocrm_lead_id:
            amo_client = AmoCRMClient()
            
            # Маппинг статусов
            status_mapping = {
                "new": 1,
                "contacted": 2,
                "presentation": 3,
                "object_selected": 4,
                "reserved": 5,
                "deal": 6,
                "completed": 7
            }
            
            amo_status_id = status_mapping.get(status)
            if amo_status_id:
                await amo_client.update_lead_status(lead.amocrm_lead_id, amo_status_id)
        
        return {"status": "success", "message": f"Lead status updated to {status}"}
        
    except Exception as e:
        logger.error(f"Error updating lead status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update lead status: {str(e)}")

@router.get("/{lead_id}/amo")
async def get_lead_amo_info(lead_id: int, db: Session = Depends(get_db)):
    """
    Получение информации о лиде из amoCRM
    """
    try:
        from app.models.lead import Lead
        
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        if not lead.amocrm_lead_id:
            raise HTTPException(status_code=404, detail="Lead not synced with amoCRM")
        
        amo_client = AmoCRMClient()
        
        # Получаем информацию о сделке
        amo_lead = await amo_client.get_lead(lead.amocrm_lead_id)
        
        if not amo_lead:
            raise HTTPException(status_code=404, detail="Lead not found in amoCRM")
        
        # Получаем информацию о контакте
        amo_contact = None
        if lead.amocrm_contact_id:
            amo_contact = await amo_client.get_contact(lead.amocrm_contact_id)
        
        return {
            "lead": amo_lead,
            "contact": amo_contact
        }
        
    except Exception as e:
        logger.error(f"Error getting amo info for lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get amo info: {str(e)}")
