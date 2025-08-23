import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.core.db import get_db
from app.models.amocrm_token import AmoCRMToken

class AmoCRMAuth:
    def __init__(self):
        self.base_url = f"https://{settings.amocrm_domain}" if settings.amocrm_domain else "https://your-domain.amocrm.ru"
        self.client_id = settings.amocrm_client_id
        self.client_secret = settings.amocrm_client_secret
        self.redirect_uri = settings.amocrm_redirect_uri
    
    def get_auth_url(self) -> str:
        """Генерация URL для OAuth2 авторизации"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": "random_state_string"  # В продакшене использовать secure random
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}/oauth2/authorize?{query_string}"
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Обмен authorization code на access и refresh токены"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth2/access_token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.redirect_uri
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info("Successfully exchanged code for tokens")
                return data
                
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {str(e)}")
            raise
    
    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Обновление access token с помощью refresh token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth2/access_token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info("Successfully refreshed tokens")
                return data
                
        except Exception as e:
            logger.error(f"Error refreshing tokens: {str(e)}")
            raise
    
    async def save_tokens(self, tokens: Dict[str, Any]) -> bool:
        """Сохранение токенов в БД"""
        try:
            db = next(get_db())
            
            # Деактивируем старые токены
            old_tokens = db.query(AmoCRMToken).filter(AmoCRMToken.is_active == True).all()
            for token in old_tokens:
                token.is_active = False
            
            # Вычисляем время истечения токена
            expires_in = tokens.get("expires_in", 86400)  # 24 часа по умолчанию
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Создаем новый токен
            new_token = AmoCRMToken(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                expires_at=expires_at,
                token_type=tokens.get("token_type", "Bearer"),
                scope=tokens.get("scope"),
                account_id=tokens.get("account_id")
            )
            
            db.add(new_token)
            db.commit()
            db.refresh(new_token)
            
            logger.info(f"Tokens saved successfully: access_token={tokens.get('access_token', '')[:10]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error saving tokens: {str(e)}")
            return False
    
    async def get_stored_tokens(self) -> Optional[Dict[str, Any]]:
        """Получение сохраненных токенов из БД"""
        try:
            db = next(get_db())
            token = db.query(AmoCRMToken).filter(
                AmoCRMToken.is_active == True
            ).first()
            
            if token and not token.is_expired():
                return token.to_dict()
            elif token and token.is_expired():
                # Обновляем истекший токен
                return await self._refresh_stored_token(token)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting stored tokens: {str(e)}")
            return None
    
    async def _refresh_stored_token(self, token: AmoCRMToken) -> Optional[Dict[str, Any]]:
        """Обновление истекшего токена"""
        try:
            new_tokens = await self.refresh_tokens(token.refresh_token)
            await self.save_tokens(new_tokens)
            return new_tokens
            
        except Exception as e:
            logger.error(f"Error refreshing stored token: {str(e)}")
            return None
    
    async def revoke_tokens(self, access_token: str) -> bool:
        """Отзыв токенов"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth2/revoke",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "token": access_token
                    }
                )
                response.raise_for_status()
                
                # Деактивируем токен в БД
                db = next(get_db())
                token = db.query(AmoCRMToken).filter(
                    AmoCRMToken.access_token == access_token
                ).first()
                
                if token:
                    token.is_active = False
                    db.commit()
                
                logger.info("Tokens revoked successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error revoking tokens: {str(e)}")
            return False
    
    def validate_token(self, access_token: str) -> bool:
        """Валидация access token"""
        try:
            # Простая проверка формата токена
            if not access_token or len(access_token) < 10:
                return False
            return True
            
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return False
    
    async def is_authorized(self) -> bool:
        """Проверка авторизации"""
        try:
            tokens = await self.get_stored_tokens()
            return tokens is not None
            
        except Exception as e:
            logger.error(f"Error checking authorization: {str(e)}")
            return False
