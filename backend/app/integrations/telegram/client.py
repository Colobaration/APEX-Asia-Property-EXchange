from typing import Optional
import httpx
from app.core.config import settings
from app.core.logging import logger


class TelegramClient:
    """Minimal Telegram Bot API client using HTTP requests only.

    Requires:
    - settings.telegram_bot_token
    - settings.telegram_default_chat_id (optional fallback)
    """

    def __init__(self, bot_token: Optional[str] = None) -> None:
        self.bot_token = bot_token or settings.telegram_bot_token
        if not self.bot_token:
            logger.warning("Telegram bot token is not configured")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None

    async def send_message(self, text: str, chat_id: Optional[str] = None) -> dict:
        if not self.base_url:
            raise RuntimeError("Telegram bot token missing. Set TELEGRAM_BOT_TOKEN in environment.")
        target_chat_id = chat_id or settings.telegram_default_chat_id
        if not target_chat_id:
            raise RuntimeError("Telegram chat_id is required (provide in request or TELEGRAM_DEFAULT_CHAT_ID).")

        payload = {
            "chat_id": target_chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{self.base_url}/sendMessage", json=payload)
            try:
                response.raise_for_status()
            except Exception as exc:
                logger.error(f"Telegram sendMessage failed: {response.text}")
                raise exc
            return response.json()


