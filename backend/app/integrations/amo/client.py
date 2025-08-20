import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.logging import logger
from app.integrations.amo.auth import AmoCRMAuth

class AmoCRMClient:
    def __init__(self):
        self.base_url = f"https://{settings.amocrm_domain}" if settings.amocrm_domain else "https://your-domain.amocrm.ru"
        self.auth_client = AmoCRMAuth()
        self.access_token = None
        self.refresh_token = None
        
    async def _get_access_token(self) -> str:
        """Получение актуального access token"""
        if not self.access_token:
            await self._refresh_access_token()
        return self.access_token
    
    async def _refresh_access_token(self):
        """Обновление access token"""
        try:
            # Получаем токены из БД
            tokens = await self.auth_client.get_stored_tokens()
            
            if not tokens:
                raise Exception("No stored tokens found. Please authorize first.")
            
            # Если токен истек, обновляем его
            if tokens.get("expires_at"):
                from datetime import datetime
                expires_at = datetime.fromisoformat(tokens["expires_at"])
                if datetime.utcnow() > expires_at:
                    new_tokens = await self.auth_client.refresh_tokens(tokens["refresh_token"])
                    await self.auth_client.save_tokens(new_tokens)
                    tokens = new_tokens
            
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            
            logger.info("Access token refreshed successfully")
                
        except Exception as e:
            logger.error(f"Error refreshing access token: {str(e)}")
            raise
    
    async def find_or_create_contact(
        self, 
        name: str, 
        phone: str, 
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Поиск или создание контакта в amoCRM"""
        try:
            access_token = await self._get_access_token()
            
            # Поиск существующего контакта по телефону
            contact = await self._find_contact_by_phone(phone, access_token)
            
            if contact:
                # Обновление существующего контакта
                return await self._update_contact(contact["id"], name, email, access_token)
            else:
                # Создание нового контакта
                return await self._create_contact(name, phone, email, access_token)
                
        except Exception as e:
            logger.error(f"Error in find_or_create_contact: {str(e)}")
            raise
    
    async def _find_contact_by_phone(self, phone: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Поиск контакта по телефону"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v4/contacts",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"query": phone}
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("_embedded", {}).get("contacts"):
                    return data["_embedded"]["contacts"][0]
                return None
                
        except Exception as e:
            logger.error(f"Error finding contact by phone: {str(e)}")
            return None
    
    async def _create_contact(
        self, 
        name: str, 
        phone: str, 
        email: Optional[str], 
        access_token: str
    ) -> Dict[str, Any]:
        """Создание нового контакта"""
        contact_data = {
            "name": name,
            "custom_fields_values": [
                {
                    "field_id": 123456,  # ID поля телефона
                    "values": [{"value": phone, "enum_code": "WORK"}]
                }
            ]
        }
        
        if email:
            contact_data["custom_fields_values"].append({
                "field_id": 123457,  # ID поля email
                "values": [{"value": email, "enum_code": "WORK"}]
            })
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v4/contacts",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=[contact_data]
                )
                response.raise_for_status()
                data = response.json()
                
                return data["_embedded"]["contacts"][0]
                
        except Exception as e:
            logger.error(f"Error creating contact: {str(e)}")
            raise
    
    async def _update_contact(
        self, 
        contact_id: int, 
        name: str, 
        email: Optional[str], 
        access_token: str
    ) -> Dict[str, Any]:
        """Обновление существующего контакта"""
        update_data = {"name": name}
        
        if email:
            update_data["custom_fields_values"] = [{
                "field_id": 123457,  # ID поля email
                "values": [{"value": email, "enum_code": "WORK"}]
            }]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/api/v4/contacts/{contact_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=update_data
                )
                response.raise_for_status()
                data = response.json()
                
                return data
                
        except Exception as e:
            logger.error(f"Error updating contact: {str(e)}")
            raise
    
    async def create_lead(
        self, 
        contact_id: int, 
        name: str, 
        utm_data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Создание сделки в amoCRM"""
        try:
            access_token = await self._get_access_token()
            
            lead_data = {
                "name": name,
                "_embedded": {
                    "contacts": [{"id": contact_id}]
                },
                "custom_fields_values": []
            }
            
            # Добавление UTM меток
            if utm_data:
                for utm_key, utm_value in utm_data.items():
                    if utm_value:
                        field_id = self._get_utm_field_id(utm_key)
                        if field_id:
                            lead_data["custom_fields_values"].append({
                                "field_id": field_id,
                                "values": [{"value": utm_value}]
                            })
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v4/leads",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=[lead_data]
                )
                response.raise_for_status()
                data = response.json()
                
                return data["_embedded"]["leads"][0]
                
        except Exception as e:
            logger.error(f"Error creating lead: {str(e)}")
            raise
    
    async def update_lead_status(
        self, 
        lead_id: int, 
        status_id: int
    ) -> Dict[str, Any]:
        """Обновление статуса сделки"""
        try:
            access_token = await self._get_access_token()
            
            update_data = {
                "status_id": status_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/api/v4/leads/{lead_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=update_data
                )
                response.raise_for_status()
                data = response.json()
                
                return data
                
        except Exception as e:
            logger.error(f"Error updating lead status: {str(e)}")
            raise
    
    async def get_lead(self, lead_id: int) -> Optional[Dict[str, Any]]:
        """Получение информации о сделке"""
        try:
            access_token = await self._get_access_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v4/leads/{lead_id}",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                data = response.json()
                
                return data
                
        except Exception as e:
            logger.error(f"Error getting lead: {str(e)}")
            return None
    
    async def get_contact(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """Получение информации о контакте"""
        try:
            access_token = await self._get_access_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v4/contacts/{contact_id}",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                data = response.json()
                
                return data
                
        except Exception as e:
            logger.error(f"Error getting contact: {str(e)}")
            return None
    
    async def add_tag_to_lead(self, lead_id: int, tag_name: str) -> bool:
        """Добавление тега к сделке"""
        try:
            access_token = await self._get_access_token()
            
            # Сначала создаем тег, если его нет
            tag_id = await self._get_or_create_tag(tag_name, access_token)
            
            # Добавляем тег к сделке
            update_data = {
                "_embedded": {
                    "tags": [{"id": tag_id}]
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/api/v4/leads/{lead_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=update_data
                )
                response.raise_for_status()
                
                return True
                
        except Exception as e:
            logger.error(f"Error adding tag to lead: {str(e)}")
            return False
    
    async def _get_or_create_tag(self, tag_name: str, access_token: str) -> int:
        """Получение или создание тега"""
        try:
            # Поиск существующего тега
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v4/leads/note_types",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                data = response.json()
                
                # Поиск тега по имени
                for tag in data.get("_embedded", {}).get("note_types", []):
                    if tag["name"] == tag_name:
                        return tag["id"]
                
                # Создание нового тега
                tag_data = {"name": tag_name}
                response = await client.post(
                    f"{self.base_url}/api/v4/leads/note_types",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=[tag_data]
                )
                response.raise_for_status()
                data = response.json()
                
                return data["_embedded"]["note_types"][0]["id"]
                
        except Exception as e:
            logger.error(f"Error getting or creating tag: {str(e)}")
            raise
    
    def _get_utm_field_id(self, utm_key: str) -> int:
        """Получение ID поля для UTM метки"""
        utm_field_ids = {
            "utm_source": 123458,
            "utm_medium": 123459,
            "utm_campaign": 123460,
            "utm_content": 123461,
            "utm_term": 123462
        }
        return utm_field_ids.get(utm_key, 0)
    
    async def test_connection(self) -> bool:
        """Тестирование подключения к amoCRM"""
        try:
            access_token = await self._get_access_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v4/account",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                
                return True
                
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Получение информации об аккаунте"""
        try:
            access_token = await self._get_access_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v4/account",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                data = response.json()
                
                return data
                
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return None
