from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.db import get_db
from app.models.lead import Lead
from app.integrations.amo.client import AmoCRMClient

router = APIRouter()

class LeadCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None

class LeadResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str]
    amocrm_contact_id: Optional[int]
    amocrm_lead_id: Optional[int]
    status: str

@router.post("/", response_model=LeadResponse)
async def create_lead(lead_data: LeadCreate, db: Session = Depends(get_db)):
    """
    Создание нового лида с валидацией и интеграцией в amoCRM
    """
    try:
        # Создание лида в локальной БД
        db_lead = Lead(
            name=lead_data.name,
            phone=lead_data.phone,
            email=lead_data.email,
            utm_source=lead_data.utm_source,
            utm_medium=lead_data.utm_medium,
            utm_campaign=lead_data.utm_campaign,
            utm_content=lead_data.utm_content,
            utm_term=lead_data.utm_term
        )
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        
        # Интеграция с amoCRM
        amo_client = AmoCRMClient()
        
        # Поиск или создание контакта
        contact = await amo_client.find_or_create_contact(
            name=lead_data.name,
            phone=lead_data.phone,
            email=lead_data.email
        )
        
        # Создание сделки
        lead = await amo_client.create_lead(
            contact_id=contact["id"],
            name=f"Лид: {lead_data.name}",
            utm_data={
                "utm_source": lead_data.utm_source,
                "utm_medium": lead_data.utm_medium,
                "utm_campaign": lead_data.utm_campaign,
                "utm_content": lead_data.utm_content,
                "utm_term": lead_data.utm_term
            }
        )
        
        # Обновление записи в БД
        db_lead.amocrm_contact_id = contact["id"]
        db_lead.amocrm_lead_id = lead["id"]
        db_lead.status = "created"
        db.commit()
        
        return LeadResponse(
            id=db_lead.id,
            name=db_lead.name,
            phone=db_lead.phone,
            email=db_lead.email,
            amocrm_contact_id=db_lead.amocrm_contact_id,
            amocrm_lead_id=db_lead.amocrm_lead_id,
            status=db_lead.status
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Получение информации о лиде
    """
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
        status=lead.status
    )
