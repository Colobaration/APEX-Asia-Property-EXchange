from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional, List, Union
import os
import json

class Settings(BaseSettings):
    # Основные настройки
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # amoCRM настройки
    amocrm_client_id: Optional[str] = None
    amocrm_client_secret: Optional[str] = None
    amocrm_redirect_uri: str = "http://localhost:8000/api/auth/amo/callback"
    amocrm_refresh_token: Optional[str] = None
    amocrm_domain: Optional[str] = None
    amocrm_webhook_secret: Optional[str] = None
    
    # База данных
    db_url: str = "postgresql://asia:asia@db:5432/asia_crm_staging"
    database_url: Optional[str] = None
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # Redis
    redis_url: str = "redis://redis:6379"
    redis_db: int = 0
    
    # Frontend URL
    frontend_url: str = "http://localhost:3000"
    
    # Безопасность
    secret_key: str = "your-staging-secret-key"
    jwt_secret: str = "your-staging-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # CORS
    allowed_hosts_raw: str = "*"  # Сырая строка из переменной окружения
    cors_origins_raw: str = "*"   # Сырая строка из переменной окружения
    
    @property
    def allowed_hosts(self) -> List[str]:
        """Возвращает список разрешенных хостов"""
        if self.allowed_hosts_raw == "*":
            return ["*"]
        return [host.strip() for host in self.allowed_hosts_raw.split(",") if host.strip()]
    
    @property
    def cors_origins(self) -> List[str]:
        """Возвращает список разрешенных CORS origins"""
        if self.cors_origins_raw == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]
    
    # Email настройки
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    email_from: Optional[str] = None
    
    # WhatsApp настройки
    whatsapp_api_url: Optional[str] = None
    whatsapp_api_key: Optional[str] = None
    whatsapp_phone_number: Optional[str] = None

    # Telegram настройки
    telegram_bot_token: Optional[str] = None
    telegram_default_chat_id: Optional[str] = None
    
    # API настройки
    api_prefix: str = "/api"
    api_version: str = "v1"
    
    # Мониторинг
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Логирование
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    
    # Кэширование
    cache_ttl: int = 3600  # 1 час
    cache_prefix: str = "apex:"
    
    # Уведомления
    notification_queue: str = "notifications"
    notification_retry_attempts: int = 3
    
    # Интеграции
    enable_amocrm: bool = True
    enable_email: bool = False
    enable_whatsapp: bool = False
    enable_telegram: bool = False
    
    model_config = SettingsConfigDict(
        # env_file=".env.staging" if os.getenv("ENVIRONMENT") == "staging" else ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Используем DATABASE_URL если он указан
        if self.database_url:
            self.db_url = self.database_url

settings = Settings()
