from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.core.db import get_db
from app.models.lead import Lead
from app.integrations.amo.webhooks import AmoCRMWebhookHandler
from app.core.logging import logger

router = APIRouter()

class WebhookData(BaseModel):
    leads: Optional[Dict[str, Any]] = None
    contacts: Optional[Dict[str, Any]] = None
    account: Optional[Dict[str, Any]] = None

@router.post("/amo")
async def amo_webhook(
    webhook_data: WebhookData,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Обработка webhooks от amoCRM
    """
    try:
        # Логирование входящего webhook
        logger.info(f"Received amoCRM webhook: {webhook_data}")
        
        webhook_handler = AmoCRMWebhookHandler()
        
        # Обработка изменений лидов
        if webhook_data.leads:
            await webhook_handler.handle_leads_update(
                leads_data=webhook_data.leads,
                db=db
            )
        
        # Обработка изменений контактов
        if webhook_data.contacts:
            await webhook_handler.handle_contacts_update(
                contacts_data=webhook_data.contacts,
                db=db
            )
        
        return {"status": "success", "message": "Webhook processed"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/amo/lead-status-changed")
async def lead_status_changed(
    lead_id: int,
    status_id: int,
    db: Session = Depends(get_db)
):
    """
    Обработка изменения статуса сделки
    """
    try:
        # Поиск лида в БД
        lead = db.query(Lead).filter(Lead.amocrm_lead_id == lead_id).first()
        if not lead:
            logger.warning(f"Lead with amoCRM ID {lead_id} not found in local DB")
            return {"status": "warning", "message": "Lead not found"}
        
        # Обновление статуса
        lead.status = f"status_{status_id}"
        db.commit()
        
        # Логирование изменения
        logger.info(f"Lead {lead_id} status changed to {status_id}")
        
        return {"status": "success", "message": "Status updated"}
        
    except Exception as e:
        logger.error(f"Error updating lead status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/amo/lead-created")
async def lead_created(
    lead_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Обработка создания новой сделки в amoCRM
    """
    try:
        webhook_handler = AmoCRMWebhookHandler()
        await webhook_handler.handle_lead_created(lead_data, db)
        
        return {"status": "success", "message": "Lead creation processed"}
        
    except Exception as e:
        logger.error(f"Error processing lead creation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
