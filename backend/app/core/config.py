from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # amoCRM настройки
    amocrm_client_id: str
    amocrm_client_secret: str
    amocrm_redirect_uri: str = "http://localhost:8000/api/auth/amo/callback"
    amocrm_refresh_token: Optional[str] = None
    amocrm_domain: Optional[str] = None
    
    # База данных
    db_url: str = "postgresql://asia:asia@db:5432/asia_crm"
    
    # Frontend URL
    frontend_url: str = "http://localhost:3000"
    
    # Безопасность
    secret_key: str
    jwt_secret: str
    
    # Email настройки
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # WhatsApp настройки
    whatsapp_api_url: Optional[str] = None
    whatsapp_api_key: Optional[str] = None

    # Telegram настройки
    telegram_bot_token: Optional[str] = None
    telegram_default_chat_id: Optional[str] = None
    
    # Логирование
    log_level: str = "INFO"
    
    # Безопасность
    debug: bool = False
    allowed_hosts: list = ["localhost", "127.0.0.1"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
