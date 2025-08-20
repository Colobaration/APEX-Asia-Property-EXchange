from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # amoCRM настройки
    amocrm_client_id: str
    amocrm_client_secret: str
    amocrm_redirect_uri: str
    amocrm_refresh_token: Optional[str] = None
    
    # База данных
    db_url: str = "postgresql://asia:asia@db:5432/asia_crm"
    
    # Безопасность
    secret_key: str = "your-secret-key-here"
    jwt_secret: str = "your-jwt-secret-here"
    
    # Email настройки
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # WhatsApp настройки
    whatsapp_api_url: Optional[str] = None
    whatsapp_api_key: Optional[str] = None
    
    # Логирование
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
