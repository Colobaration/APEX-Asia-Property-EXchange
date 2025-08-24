"""
Dependency injection для FastAPI
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.config import settings
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.exceptions import AuthenticationError

# Схема безопасности для JWT токенов
security = HTTPBearer()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Получение сервиса аутентификации"""
    return AuthService(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Получение текущего пользователя по JWT токену"""
    try:
        token = credentials.credentials
        user = auth_service.get_current_user(token)
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Получение текущего активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивный пользователь"
        )
    return current_user


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Получение текущего суперпользователя"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """Получение текущего пользователя (опционально)"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = auth_service.get_current_user(token)
        return user
    except AuthenticationError:
        return None


def get_pagination_params(
    page: int = 1,
    per_page: int = 20
) -> dict:
    """Параметры пагинации"""
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20
    
    return {
        "page": page,
        "per_page": per_page,
        "offset": (page - 1) * per_page
    }


def get_search_params(
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc"
) -> dict:
    """Параметры поиска и сортировки"""
    return {
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order.lower() if sort_order else "asc"
    }


def validate_api_key(api_key: Optional[str] = None) -> bool:
    """Валидация API ключа для webhook'ов"""
    if not api_key:
        return False
    
    # Здесь можно добавить логику валидации API ключа
    # Например, проверка против списка разрешенных ключей
    return api_key == settings.amocrm_webhook_secret


def get_webhook_auth(
    api_key: Optional[str] = None
) -> bool:
    """Аутентификация для webhook'ов"""
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный API ключ"
        )
    return True
