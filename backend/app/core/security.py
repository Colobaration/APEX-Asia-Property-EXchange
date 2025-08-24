"""
Модуль безопасности для аутентификации и авторизации
"""

from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import hashlib
import hmac

from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User

# Схема безопасности для JWT токенов
security = HTTPBearer()

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityUtils:
    """Утилиты для безопасности"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Создание JWT токена"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Проверка JWT токена"""
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            return payload
        except JWTError:
            return None

    @staticmethod
    def generate_api_key() -> str:
        """Генерация API ключа"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Хеширование API ключа"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
        """Проверка подписи webhook"""
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

    @staticmethod
    def generate_idempotency_key() -> str:
        """Генерация ключа идемпотентности"""
        return secrets.token_urlsafe(16)


class RateLimiter:
    """Rate limiter для API запросов"""

    def __init__(self):
        self.requests = {}  # В реальном проекте используется Redis

    def is_allowed(self, client_id: str, limit: int = 100, window: int = 3600) -> bool:
        """Проверка лимита запросов"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window)
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Удаляем старые запросы
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Проверяем лимит
        if len(self.requests[client_id]) >= limit:
            return False
        
        # Добавляем новый запрос
        self.requests[client_id].append(now)
        return True


# Глобальный экземпляр rate limiter
rate_limiter = RateLimiter()


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = None  # Здесь должна быть зависимость для БД
) -> User:
    """Получение текущего пользователя из JWT токена"""
    try:
        payload = SecurityUtils.verify_token(credentials.credentials)
        if payload is None:
            raise AuthenticationError("Недействительный токен")
        
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Недействительный токен")
        
        # Здесь должна быть логика получения пользователя из БД
        # user = get_user_by_id(user_id, db)
        # if user is None:
        #     raise AuthenticationError("Пользователь не найден")
        # if not user.is_active:
        #     raise AuthenticationError("Пользователь неактивен")
        
        # Временно возвращаем заглушку
        return None
        
    except AuthenticationError:
        raise
    except Exception as e:
        raise AuthenticationError(f"Ошибка аутентификации: {str(e)}")


async def get_current_active_user(
    current_user: User = Depends(get_current_user_from_token)
) -> User:
    """Получение текущего активного пользователя"""
    if not current_user or not current_user.is_active:
        raise AuthenticationError("Пользователь неактивен")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Получение текущего суперпользователя"""
    if not current_user.is_superuser:
        raise AuthorizationError("Недостаточно прав")
    return current_user


def require_permissions(permissions: List[str]):
    """Декоратор для проверки прав доступа"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Здесь должна быть логика проверки прав
            # Пока просто пропускаем
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def check_rate_limit(request: Request, limit: int = 100, window: int = 3600):
    """Проверка rate limit для запроса"""
    client_id = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_id, limit, window):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Превышен лимит запросов"
        )


def validate_cors_origin(origin: str) -> bool:
    """Валидация CORS origin"""
    allowed_origins = settings.cors_origins
    if "*" in allowed_origins:
        return True
    
    return origin in allowed_origins


def sanitize_input(input_str: str) -> str:
    """Очистка пользовательского ввода"""
    # Базовая очистка от XSS
    dangerous_chars = ["<", ">", '"', "'", "&"]
    for char in dangerous_chars:
        input_str = input_str.replace(char, "")
    
    return input_str.strip()


def validate_file_upload(filename: str, max_size: int = 10 * 1024 * 1024) -> bool:
    """Валидация загружаемого файла"""
    # Проверка расширения
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx']
    file_ext = filename.lower().split('.')[-1]
    
    if f'.{file_ext}' not in allowed_extensions:
        return False
    
    # Размер файла проверяется на уровне middleware
    return True
