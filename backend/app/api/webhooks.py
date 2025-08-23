from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.logging import logger
from app.integrations.amo.auth import AmoCRMAuth
from typing import Dict, Any, Optional
import hashlib
import hmac
import json
from datetime import datetime
from pydantic import BaseModel, ValidationError

router = APIRouter()

# Модели для валидации webhook данных
class WebhookEvent(BaseModel):
    """Модель для валидации webhook события"""
    event_type: str
    data: Dict[str, Any]
    timestamp: Optional[datetime] = None

class WebhookResponse(BaseModel):
    """Модель для ответа webhook"""
    status: str
    message: str
    events_processed: int
    timestamp: datetime
    errors: Optional[list] = None

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
        if not all([client_uuid, signature, account_id, client_secret]):
            logger.warning("Missing required webhook signature parameters")
            return False
            
        # Создаем подпись для проверки
        message = f"{client_uuid}|{account_id}"
        expected_signature = hmac.new(
            client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if is_valid:
            logger.info(f"Webhook signature verified for account: {account_id}")
        else:
            logger.warning(f"Invalid webhook signature for account: {account_id}")
            
        return is_valid
        
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False

def validate_webhook_data(body: Dict[str, Any]) -> bool:
    """
    Валидация структуры webhook данных
    """
    try:
        required_sections = ["leads", "contacts"]
        has_valid_section = False
        
        for section in required_sections:
            if section in body and isinstance(body[section], dict):
                has_valid_section = True
                # Проверяем, что есть хотя бы один тип события
                event_types = ["add", "update", "delete"]
                for event_type in event_types:
                    if event_type in body[section]:
                        if not isinstance(body[section][event_type], list):
                            logger.warning(f"Invalid {section}.{event_type} format - expected list")
                            return False
        
        if not has_valid_section:
            logger.warning("No valid sections found in webhook data")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating webhook data: {str(e)}")
        return False

@router.post("/amo")
async def amo_webhook(
    request: Request,
    client_uuid: Optional[str] = Header(None, alias="X-Client-UUID"),
    signature: Optional[str] = Header(None, alias="X-Signature"),
    account_id: Optional[str] = Header(None, alias="X-Account-ID"),
    db: Session = Depends(get_db)
):
    """
    Обработка webhook от amoCRM
    
    Поддерживаемые события:
    - leads.add - создание новых лидов
    - leads.update - обновление лидов
    - leads.delete - удаление лидов
    - contacts.add - создание новых контактов
    - contacts.update - обновление контактов
    """
    start_time = datetime.utcnow()
    errors = []
    events_processed = 0
    
    try:
        # Получаем тело запроса
        body = await request.json()
        logger.info(f"Received webhook from amoCRM: {json.dumps(body, default=str)[:500]}...")
        
        # Валидируем структуру данных
        if not validate_webhook_data(body):
            raise HTTPException(status_code=400, detail="Invalid webhook data structure")
        
        # Проверяем подлинность webhook
        auth_client = AmoCRMAuth()
        
        if not verify_webhook_signature(
            client_uuid,
            signature,
            account_id,
            auth_client.client_secret
        ):
            logger.warning(f"Invalid webhook signature from account: {account_id}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Обрабатываем события
        try:
            # Обработка событий лидов
            if "leads" in body:
                lead_events = await _process_lead_events(body["leads"], db)
                events_processed += lead_events["processed"]
                errors.extend(lead_events.get("errors", []))
            
            # Обработка событий контактов
            if "contacts" in body:
                contact_events = await _process_contact_events(body["contacts"], db)
                events_processed += contact_events["processed"]
                errors.extend(contact_events.get("errors", []))
                
        except Exception as e:
            error_msg = f"Error processing webhook events: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Формируем ответ
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Webhook processed {events_processed} events in {processing_time:.2f}s")
        
        response = WebhookResponse(
            status="success" if not errors else "partial_success",
            message=f"Processed {events_processed} events",
            events_processed=events_processed,
            timestamp=datetime.utcnow(),
            errors=errors if errors else None
        )
        
        return response.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error processing webhook: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

async def _process_lead_events(leads_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Обработка событий лидов
    """
    events_processed = 0
    errors = []
    
    try:
        from app.models.lead import Lead
        
        # Обработка новых лидов
        if "add" in leads_data:
            for lead_data in leads_data["add"]:
                try:
                    await _process_new_lead(lead_data, db)
                    events_processed += 1
                except Exception as e:
                    error_msg = f"Error processing new lead {lead_data.get('id', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        
        # Обработка обновлений лидов
        if "update" in leads_data:
            for lead_data in leads_data["update"]:
                try:
                    await _process_lead_update(lead_data, db)
                    events_processed += 1
                except Exception as e:
                    error_msg = f"Error processing lead update {lead_data.get('id', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        
        # Обработка удалений лидов
        if "delete" in leads_data:
            for lead_data in leads_data["delete"]:
                try:
                    await _process_lead_delete(lead_data, db)
                    events_processed += 1
                except Exception as e:
                    error_msg = f"Error processing lead delete {lead_data.get('id', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                
    except Exception as e:
        error_msg = f"Error processing lead events: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
    
    return {
        "processed": events_processed,
        "errors": errors
    }

async def _process_contact_events(contacts_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Обработка событий контактов
    """
    events_processed = 0
    errors = []
    
    try:
        from app.models.lead import Lead
        
        # Обработка новых контактов
        if "add" in contacts_data:
            for contact_data in contacts_data["add"]:
                try:
                    await _process_new_contact(contact_data, db)
                    events_processed += 1
                except Exception as e:
                    error_msg = f"Error processing new contact {contact_data.get('id', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        
        # Обработка обновлений контактов
        if "update" in contacts_data:
            for contact_data in contacts_data["update"]:
                try:
                    await _process_contact_update(contact_data, db)
                    events_processed += 1
                except Exception as e:
                    error_msg = f"Error processing contact update {contact_data.get('id', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                
    except Exception as e:
        error_msg = f"Error processing contact events: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
    
    return {
        "processed": events_processed,
        "errors": errors
    }

async def _process_new_lead(lead_data: Dict[str, Any], db: Session):
    """
    Обработка нового лида из amoCRM
    """
    try:
        from app.models.lead import Lead
        
        lead_id = lead_data.get("id")
        if not lead_id:
            raise ValueError("Lead ID is required")
        
        # Проверяем, есть ли уже такой лид в нашей БД
        existing_lead = db.query(Lead).filter(
            Lead.amocrm_lead_id == lead_id
        ).first()
        
        if existing_lead:
            logger.info(f"Lead {lead_id} already exists in local DB")
            return
        
        # Получаем информацию о контакте
        contact_id = None
        if "_embedded" in lead_data and "contacts" in lead_data["_embedded"]:
            contact_id = lead_data["_embedded"]["contacts"][0]["id"]
        
        # Извлекаем UTM метки из кастомных полей
        utm_data = _extract_utm_data(lead_data)
        
        # Создаем новый лид в локальной БД
        new_lead = Lead(
            name=lead_data.get("name", "Новый лид"),
            phone="",  # Будет заполнено из контакта
            email="",  # Будет заполнено из контакта
            amocrm_contact_id=contact_id,
            amocrm_lead_id=lead_id,
            status=_map_amo_status(lead_data.get("status_id", 1)),
            source="amocrm_webhook",
            utm_source=utm_data.get("utm_source"),
            utm_medium=utm_data.get("utm_medium"),
            utm_campaign=utm_data.get("utm_campaign"),
            utm_content=utm_data.get("utm_content"),
            utm_term=utm_data.get("utm_term"),
            created_at=lead_data.get("created_at")
        )
        
        db.add(new_lead)
        db.commit()
        
        logger.info(f"New lead created from amoCRM: {lead_id}")
        
    except Exception as e:
        logger.error(f"Error processing new lead: {str(e)}")
        raise

async def _process_lead_update(lead_data: Dict[str, Any], db: Session):
    """
    Обработка обновления лида из amoCRM
    """
    try:
        from app.models.lead import Lead
        
        lead_id = lead_data.get("id")
        if not lead_id:
            raise ValueError("Lead ID is required")
        
        # Находим лид в локальной БД
        lead = db.query(Lead).filter(
            Lead.amocrm_lead_id == lead_id
        ).first()
        
        if not lead:
            logger.warning(f"Lead {lead_id} not found in local DB")
            return
        
        # Обновляем статус
        if "status_id" in lead_data:
            lead.status = _map_amo_status(lead_data["status_id"])
        
        # Обновляем название
        if "name" in lead_data:
            lead.name = lead_data["name"]
        
        # Обновляем UTM метки
        utm_data = _extract_utm_data(lead_data)
        if utm_data.get("utm_source"):
            lead.utm_source = utm_data["utm_source"]
        if utm_data.get("utm_medium"):
            lead.utm_medium = utm_data["utm_medium"]
        if utm_data.get("utm_campaign"):
            lead.utm_campaign = utm_data["utm_campaign"]
        if utm_data.get("utm_content"):
            lead.utm_content = utm_data["utm_content"]
        if utm_data.get("utm_term"):
            lead.utm_term = utm_data["utm_term"]
        
        db.commit()
        
        logger.info(f"Lead updated from amoCRM: {lead_id}")
        
    except Exception as e:
        logger.error(f"Error processing lead update: {str(e)}")
        raise

async def _process_lead_delete(lead_data: Dict[str, Any], db: Session):
    """
    Обработка удаления лида из amoCRM
    """
    try:
        from app.models.lead import Lead
        
        lead_id = lead_data.get("id")
        if not lead_id:
            raise ValueError("Lead ID is required")
        
        # Находим лид в локальной БД
        lead = db.query(Lead).filter(
            Lead.amocrm_lead_id == lead_id
        ).first()
        
        if not lead:
            logger.warning(f"Lead {lead_id} not found in local DB")
            return
        
        # Помечаем как удаленный
        lead.status = "deleted"
        db.commit()
        
        logger.info(f"Lead marked as deleted from amoCRM: {lead_id}")
        
    except Exception as e:
        logger.error(f"Error processing lead delete: {str(e)}")
        raise

async def _process_new_contact(contact_data: Dict[str, Any], db: Session):
    """
    Обработка нового контакта из amoCRM
    """
    try:
        from app.models.lead import Lead
        
        contact_id = contact_data.get("id")
        if not contact_id:
            raise ValueError("Contact ID is required")
        
        # Находим лиды с этим контактом
        leads = db.query(Lead).filter(
            Lead.amocrm_contact_id == contact_id
        ).all()
        
        if not leads:
            logger.info(f"No leads found for contact {contact_id}")
            return
        
        # Обновляем информацию о контакте
        for lead in leads:
            if "name" in contact_data:
                lead.name = contact_data["name"]
            
            # Обновляем телефон и email из кастомных полей
            if "custom_fields_values" in contact_data:
                for field in contact_data["custom_fields_values"]:
                    field_id = field.get("field_id")
                    if field_id == 123456:  # ID поля телефона
                        if field.get("values") and len(field["values"]) > 0:
                            lead.phone = field["values"][0]["value"]
                    elif field_id == 123457:  # ID поля email
                        if field.get("values") and len(field["values"]) > 0:
                            lead.email = field["values"][0]["value"]
        
        db.commit()
        
        logger.info(f"Contact information updated from amoCRM: {contact_id}")
        
    except Exception as e:
        logger.error(f"Error processing new contact: {str(e)}")
        raise

async def _process_contact_update(contact_data: Dict[str, Any], db: Session):
    """
    Обработка обновления контакта из amoCRM
    """
    try:
        from app.models.lead import Lead
        
        contact_id = contact_data.get("id")
        if not contact_id:
            raise ValueError("Contact ID is required")
        
        # Находим лиды с этим контактом
        leads = db.query(Lead).filter(
            Lead.amocrm_contact_id == contact_id
        ).all()
        
        if not leads:
            logger.info(f"No leads found for contact {contact_id}")
            return
        
        # Обновляем информацию о контакте
        for lead in leads:
            if "name" in contact_data:
                lead.name = contact_data["name"]
            
            # Обновляем телефон и email из кастомных полей
            if "custom_fields_values" in contact_data:
                for field in contact_data["custom_fields_values"]:
                    field_id = field.get("field_id")
                    if field_id == 123456:  # ID поля телефона
                        if field.get("values") and len(field["values"]) > 0:
                            lead.phone = field["values"][0]["value"]
                    elif field_id == 123457:  # ID поля email
                        if field.get("values") and len(field["values"]) > 0:
                            lead.email = field["values"][0]["value"]
        
        db.commit()
        
        logger.info(f"Contact information updated from amoCRM: {contact_id}")
        
    except Exception as e:
        logger.error(f"Error processing contact update: {str(e)}")
        raise

def _extract_utm_data(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Извлечение UTM меток из кастомных полей
    """
    utm_data = {}
    
    if "custom_fields_values" in data:
        for field in data["custom_fields_values"]:
            field_id = field.get("field_id")
            if field.get("values") and len(field["values"]) > 0:
                value = field["values"][0]["value"]
                
                # Маппинг ID полей на UTM метки
                utm_mapping = {
                    123458: "utm_source",    # UTM Source
                    123459: "utm_medium",    # UTM Medium
                    123460: "utm_campaign",  # UTM Campaign
                    123461: "utm_content",   # UTM Content
                    123462: "utm_term"       # UTM Term
                }
                
                if field_id in utm_mapping:
                    utm_data[utm_mapping[field_id]] = value
    
    return utm_data

def _map_amo_status(status_id: int) -> str:
    """
    Маппинг статусов amoCRM на внутренние статусы
    """
    status_mapping = {
        1: "new",              # Новый лид
        2: "contacted",        # Первичный контакт
        3: "presentation",     # Презентация
        4: "object_selected",  # Выбор объекта
        5: "reserved",         # Резервирование
        6: "deal",             # Сделка
        7: "completed"         # Завершено
    }
    
    return status_mapping.get(status_id, "new")

@router.get("/amo/test")
async def test_webhook():
    """
    Тестовый endpoint для проверки webhook
    """
    return {
        "status": "success",
        "message": "Webhook endpoint is working",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": "/api/webhooks/amo",
        "supported_events": [
            "leads.add",
            "leads.update", 
            "leads.delete",
            "contacts.add",
            "contacts.update"
        ]
    }

@router.get("/amo/health")
async def webhook_health():
    """
    Health check для webhook сервера
    """
    try:
        # Проверяем подключение к БД
        db = next(get_db())
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "webhook_endpoint": "active"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")
