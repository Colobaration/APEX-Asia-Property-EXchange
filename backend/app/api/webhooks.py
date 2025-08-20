from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.logging import logger
from app.integrations.amo.auth import AmoCRMAuth
from typing import Dict, Any
import hashlib
import hmac

router = APIRouter()

def verify_webhook_signature(
    client_uuid: str,
    signature: str,
    account_id: str,
    client_secret: str
) -> bool:
    """
    Проверка подлинности webhook от amoCRM
    """
    try:
        # Создаем подпись для проверки
        message = f"{client_uuid}|{account_id}"
        expected_signature = hmac.new(
            client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False

@router.post("/amo")
async def amo_webhook(
    request: Request,
    client_uuid: str = None,
    signature: str = None,
    account_id: str = None,
    db: Session = Depends(get_db)
):
    """
    Обработка webhook от amoCRM
    """
    try:
        # Получаем тело запроса
        body = await request.json()
        
        # Проверяем подлинность webhook
        auth_client = AmoCRMAuth()
        
        if not verify_webhook_signature(
            client_uuid,
            signature,
            account_id,
            auth_client.client_secret
        ):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Обрабатываем события
        events_processed = 0
        
        # Обработка событий лидов
        if "leads" in body:
            events_processed += await _process_lead_events(body["leads"], db)
        
        # Обработка событий контактов
        if "contacts" in body:
            events_processed += await _process_contact_events(body["contacts"], db)
        
        logger.info(f"Webhook processed {events_processed} events")
        
        return {"status": "success", "events_processed": events_processed}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _process_lead_events(leads_data: Dict[str, Any], db: Session) -> int:
    """
    Обработка событий лидов
    """
    events_processed = 0
    
    try:
        from app.models.lead import Lead
        
        # Обработка новых лидов
        if "add" in leads_data:
            for lead_data in leads_data["add"]:
                await _process_new_lead(lead_data, db)
                events_processed += 1
        
        # Обработка обновлений лидов
        if "update" in leads_data:
            for lead_data in leads_data["update"]:
                await _process_lead_update(lead_data, db)
                events_processed += 1
        
        # Обработка удалений лидов
        if "delete" in leads_data:
            for lead_data in leads_data["delete"]:
                await _process_lead_delete(lead_data, db)
                events_processed += 1
                
    except Exception as e:
        logger.error(f"Error processing lead events: {str(e)}")
    
    return events_processed

async def _process_contact_events(contacts_data: Dict[str, Any], db: Session) -> int:
    """
    Обработка событий контактов
    """
    events_processed = 0
    
    try:
        from app.models.lead import Lead
        
        # Обработка новых контактов
        if "add" in contacts_data:
            for contact_data in contacts_data["add"]:
                await _process_new_contact(contact_data, db)
                events_processed += 1
        
        # Обработка обновлений контактов
        if "update" in contacts_data:
            for contact_data in contacts_data["update"]:
                await _process_contact_update(contact_data, db)
                events_processed += 1
                
    except Exception as e:
        logger.error(f"Error processing contact events: {str(e)}")
    
    return events_processed

async def _process_new_lead(lead_data: Dict[str, Any], db: Session):
    """
    Обработка нового лида из amoCRM
    """
    try:
        from app.models.lead import Lead
        
        # Проверяем, есть ли уже такой лид в нашей БД
        existing_lead = db.query(Lead).filter(
            Lead.amocrm_lead_id == lead_data["id"]
        ).first()
        
        if existing_lead:
            logger.info(f"Lead {lead_data['id']} already exists in local DB")
            return
        
        # Получаем информацию о контакте
        contact_id = None
        if "_embedded" in lead_data and "contacts" in lead_data["_embedded"]:
            contact_id = lead_data["_embedded"]["contacts"][0]["id"]
        
        # Создаем новый лид в локальной БД
        new_lead = Lead(
            name=lead_data.get("name", "Новый лид"),
            phone="",  # Будет заполнено из контакта
            email="",  # Будет заполнено из контакта
            amocrm_contact_id=contact_id,
            amocrm_lead_id=lead_data["id"],
            status="new",
            created_at=lead_data.get("created_at")
        )
        
        db.add(new_lead)
        db.commit()
        
        logger.info(f"New lead created from amoCRM: {lead_data['id']}")
        
    except Exception as e:
        logger.error(f"Error processing new lead: {str(e)}")

async def _process_lead_update(lead_data: Dict[str, Any], db: Session):
    """
    Обработка обновления лида из amoCRM
    """
    try:
        from app.models.lead import Lead
        
        # Находим лид в локальной БД
        lead = db.query(Lead).filter(
            Lead.amocrm_lead_id == lead_data["id"]
        ).first()
        
        if not lead:
            logger.warning(f"Lead {lead_data['id']} not found in local DB")
            return
        
        # Обновляем статус
        if "status_id" in lead_data:
            status_mapping = {
                1: "new",
                2: "contacted",
                3: "presentation",
                4: "object_selected",
                5: "reserved",
                6: "deal",
                7: "completed"
            }
            new_status = status_mapping.get(lead_data["status_id"], "new")
            lead.status = new_status
        
        # Обновляем название
        if "name" in lead_data:
            lead.name = lead_data["name"]
        
        db.commit()
        
        logger.info(f"Lead updated from amoCRM: {lead_data['id']}")
        
    except Exception as e:
        logger.error(f"Error processing lead update: {str(e)}")

async def _process_lead_delete(lead_data: Dict[str, Any], db: Session):
    """
    Обработка удаления лида из amoCRM
    """
    try:
        from app.models.lead import Lead
        
        # Находим лид в локальной БД
        lead = db.query(Lead).filter(
            Lead.amocrm_lead_id == lead_data["id"]
        ).first()
        
        if not lead:
            logger.warning(f"Lead {lead_data['id']} not found in local DB")
            return
        
        # Помечаем как удаленный
        lead.status = "deleted"
        db.commit()
        
        logger.info(f"Lead marked as deleted from amoCRM: {lead_data['id']}")
        
    except Exception as e:
        logger.error(f"Error processing lead delete: {str(e)}")

async def _process_new_contact(contact_data: Dict[str, Any], db: Session):
    """
    Обработка нового контакта из amoCRM
    """
    try:
        from app.models.lead import Lead
        
        # Находим лиды с этим контактом
        leads = db.query(Lead).filter(
            Lead.amocrm_contact_id == contact_data["id"]
        ).all()
        
        # Обновляем информацию о контакте
        for lead in leads:
            if "name" in contact_data:
                lead.name = contact_data["name"]
            
            # Обновляем телефон и email из кастомных полей
            if "custom_fields_values" in contact_data:
                for field in contact_data["custom_fields_values"]:
                    if field["field_id"] == 123456:  # ID поля телефона
                        lead.phone = field["values"][0]["value"]
                    elif field["field_id"] == 123457:  # ID поля email
                        lead.email = field["values"][0]["value"]
        
        db.commit()
        
        logger.info(f"Contact information updated from amoCRM: {contact_data['id']}")
        
    except Exception as e:
        logger.error(f"Error processing new contact: {str(e)}")

async def _process_contact_update(contact_data: Dict[str, Any], db: Session):
    """
    Обработка обновления контакта из amoCRM
    """
    try:
        from app.models.lead import Lead
        
        # Находим лиды с этим контактом
        leads = db.query(Lead).filter(
            Lead.amocrm_contact_id == contact_data["id"]
        ).all()
        
        # Обновляем информацию о контакте
        for lead in leads:
            if "name" in contact_data:
                lead.name = contact_data["name"]
            
            # Обновляем телефон и email из кастомных полей
            if "custom_fields_values" in contact_data:
                for field in contact_data["custom_fields_values"]:
                    if field["field_id"] == 123456:  # ID поля телефона
                        lead.phone = field["values"][0]["value"]
                    elif field["field_id"] == 123457:  # ID поля email
                        lead.email = field["values"][0]["value"]
        
        db.commit()
        
        logger.info(f"Contact information updated from amoCRM: {contact_data['id']}")
        
    except Exception as e:
        logger.error(f"Error processing contact update: {str(e)}")

@router.get("/amo/test")
async def test_webhook():
    """
    Тестовый endpoint для проверки webhook
    """
    return {
        "status": "success",
        "message": "Webhook endpoint is working",
        "timestamp": "2024-01-01T00:00:00Z"
    }
