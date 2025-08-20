from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.integrations.telegram.client import TelegramClient
from app.core.logging import logger


router = APIRouter()


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


