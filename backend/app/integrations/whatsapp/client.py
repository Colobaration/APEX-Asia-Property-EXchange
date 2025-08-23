from typing import Optional
import httpx
from app.core.config import settings
from app.core.logging import logger


class WhatsAppClient:
    """Minimal WhatsApp API client (provider-agnostic placeholder).

    Expects a generic gateway at settings.whatsapp_api_url using an API key.
    Replace with provider-specific implementation later.
    """

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.api_url = api_url or settings.whatsapp_api_url
        self.api_key = api_key or settings.whatsapp_api_key
        if not self.api_url or not self.api_key:
            logger.warning("WhatsApp API url/key not configured")

    async def send_message(self, to: str, text: str) -> dict:
        if not self.api_url or not self.api_key:
            raise RuntimeError("Configure WHATSAPP_API_URL and WHATSAPP_API_KEY to use WhatsApp client")

        payload = {"to": to, "text": text}
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{self.api_url}/messages", json=payload, headers=headers)
            try:
                response.raise_for_status()
            except Exception as exc:
                logger.error(f"WhatsApp send failed: {response.text}")
                raise exc
            return response.json()


