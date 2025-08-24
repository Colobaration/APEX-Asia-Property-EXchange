"""
API роутер для аутентификации (версия 2 с сервисным слоем)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    UserUpdate,
    Token,
    LoginRequest,
    AmoCRMAuthRequest,
    AmoCRMTokenResponse
)
from app.core.dependencies import get_current_user, get_current_active_user, get_current_superuser
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 схема для JWT токенов
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя
    """
    auth_service = AuthService(db)
    user = auth_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Вход в систему
    """
    auth_service = AuthService(db)
    result = auth_service.login_user(login_data.email, login_data.password)
    return result


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение профиля текущего пользователя
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновление профиля пользователя
    """
    auth_service = AuthService(db)
    updated_user = auth_service.update_user(current_user.id, user_data)
    return updated_user


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Удаление профиля пользователя
    """
    auth_service = AuthService(db)
    auth_service.delete_user(current_user.id)


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Получение списка пользователей (только для суперпользователей)
    """
    auth_service = AuthService(db)
    # Здесь можно добавить метод для получения списка пользователей
    # Пока возвращаем пустой список
    return []


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Получение пользователя по ID (только для суперпользователей)
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Обновление пользователя (только для суперпользователей)
    """
    auth_service = AuthService(db)
    updated_user = auth_service.update_user(user_id, user_data)
    return updated_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Удаление пользователя (только для суперпользователей)
    """
    auth_service = AuthService(db)
    auth_service.delete_user(user_id)


# AmoCRM интеграция
@router.post("/amo/authorize", response_model=AmoCRMTokenResponse)
async def amo_authorize(
    auth_data: AmoCRMAuthRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Авторизация через AmoCRM OAuth2
    """
    # Здесь будет логика интеграции с AmoCRM
    # Пока возвращаем заглушку
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AmoCRM интеграция в разработке"
    )


@router.post("/amo/refresh", response_model=AmoCRMTokenResponse)
async def amo_refresh_token(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновление AmoCRM токена
    """
    # Здесь будет логика обновления AmoCRM токена
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AmoCRM интеграция в разработке"
    )


@router.get("/amo/status")
async def amo_auth_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Проверка статуса AmoCRM авторизации
    """
    # Здесь будет логика проверки статуса AmoCRM
    return {
        "authorized": False,
        "message": "AmoCRM интеграция в разработке"
    }


@router.post("/amo/revoke")
async def amo_revoke_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Отзыв AmoCRM токена
    """
    # Здесь будет логика отзыва AmoCRM токена
    return {
        "status": "success",
        "message": "AmoCRM токен отозван"
    }
