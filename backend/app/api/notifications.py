from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.integrations.telegram.client import TelegramClient
from app.integrations.whatsapp.client import WhatsAppClient
from app.integrations.email.client import EmailClient
from app.core.logging import logger

router = APIRouter()

# --- Telegram ---
class TelegramMessage(BaseModel):
    text: str
    chat_id: Optional[str] = None

@router.post("/telegram/send")
async def telegram_send(msg: TelegramMessage):
    try:
        client = TelegramClient()
        data = await client.send_message(text=msg.text, chat_id=msg.chat_id)
        return {"ok": True, "data": data}
    except Exception as exc:
        logger.exception("Telegram send failed")
        raise HTTPException(status_code=400, detail=str(exc))

# --- WhatsApp ---
class WhatsAppMessage(BaseModel):
    to: str
    text: str

@router.post("/whatsapp/send")
async def whatsapp_send(msg: WhatsAppMessage):
    try:
        client = WhatsAppClient()
        data = await client.send_message(to=msg.to, text=msg.text)
        return {"ok": True, "data": data}
    except Exception as exc:
        logger.exception("WhatsApp send failed")
        raise HTTPException(status_code=400, detail=str(exc))

# --- Email ---
class EmailMessage(BaseModel):
    to: str
    subject: str
    body: str
    from_email: Optional[str] = None

@router.post("/email/send")
async def email_send(msg: EmailMessage):
    try:
        client = EmailClient()
        client.send(
            to_email=msg.to,
            subject=msg.subject,
            body=msg.body,
            from_email=msg.from_email,
        )
        return {"ok": True}
    except Exception as exc:
        logger.exception("Email send failed")
        raise HTTPException(status_code=400, detail=str(exc))
