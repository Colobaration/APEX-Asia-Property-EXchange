from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Дополнительные поля для профиля
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Поля для аутентификации
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Поля для интеграций
    amocrm_user_id = Column(Integer, nullable=True)
    telegram_id = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    @property
    def is_locked(self):
        """Проверяет, заблокирован ли пользователь"""
        if self.locked_until and self.locked_until > func.now():
            return True
        return False
    
    def increment_failed_attempts(self):
        """Увеличивает счетчик неудачных попыток входа"""
        self.failed_login_attempts += 1
    
    def reset_failed_attempts(self):
        """Сбрасывает счетчик неудачных попыток входа"""
        self.failed_login_attempts = 0
        self.locked_until = None
