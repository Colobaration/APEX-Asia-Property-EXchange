"""
Сервис для аутентификации и авторизации
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate, TokenData
from app.core.exceptions import (
    AuthenticationError,
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError
)


class AuthService:
    """Сервис для работы с аутентификацией"""

    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Хеширование пароля"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Создание JWT токена"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Проверка JWT токена"""
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            user_id: Optional[int] = payload.get("sub")
            email: Optional[str] = payload.get("email")
            
            if user_id is None or email is None:
                return None
                
            return TokenData(user_id=user_id, email=email)
        except JWTError:
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        # Проверяем, существует ли пользователь с таким email
        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsError(f"Пользователь с email {user_data.email} уже существует")

        # Создаем нового пользователя
        hashed_password = self.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=user_data.is_active
        )
        
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise UserAlreadyExistsError(f"Пользователь с email {user_data.email} уже существует")

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Обновление пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Пользователь с ID {user_id} не найден")

        # Обновляем только переданные поля
        update_data = user_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise UserAlreadyExistsError("Пользователь с таким email уже существует")

    def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Пользователь с ID {user_id} не найден")

        self.db.delete(user)
        self.db.commit()
        return True

    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Вход пользователя в систему"""
        user = self.authenticate_user(email, password)
        if not user:
            raise InvalidCredentialsError("Неверный email или пароль")

        if not user.is_active:
            raise AuthenticationError("Пользователь неактивен")

        # Создаем токен доступа
        access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expire_minutes * 60,
            "user": user
        }

    def get_current_user(self, token: str) -> User:
        """Получение текущего пользователя по токену"""
        token_data = self.verify_token(token)
        if token_data is None:
            raise AuthenticationError("Недействительный токен")

        user = self.get_user_by_id(token_data.user_id)
        if user is None:
            raise AuthenticationError("Пользователь не найден")

        if not user.is_active:
            raise AuthenticationError("Пользователь неактивен")

        return user
