"""
Pydantic схемы для аутентификации
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Данные из JWT токена"""
    user_id: Optional[int] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Схема для входа в систему"""
    email: EmailStr
    password: str


class AmoCRMAuthRequest(BaseModel):
    """Схема для OAuth2 с AmoCRM"""
    code: str
    state: Optional[str] = None


class AmoCRMTokenResponse(BaseModel):
    """Ответ с токенами AmoCRM"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    expires_at: Optional[datetime] = None
