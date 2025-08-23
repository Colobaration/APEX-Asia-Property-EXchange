from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AmoCRMToken(Base):
    __tablename__ = "amocrm_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    token_type = Column(String, default="Bearer")
    scope = Column(String, nullable=True)
    account_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_expired(self) -> bool:
        """Проверка истечения токена"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat(),
            "token_type": self.token_type,
            "scope": self.scope,
            "account_id": self.account_id,
            "is_active": self.is_active
        }
