"""
Централизованная обработка ошибок
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class APEXException(Exception):
    """Базовый класс для всех исключений APEX"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(APEXException):
    """Ошибка аутентификации"""
    
    def __init__(self, message: str = "Ошибка аутентификации"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(APEXException):
    """Ошибка авторизации"""
    
    def __init__(self, message: str = "Недостаточно прав"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class UserNotFoundError(APEXException):
    """Пользователь не найден"""
    
    def __init__(self, message: str = "Пользователь не найден"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UserAlreadyExistsError(APEXException):
    """Пользователь уже существует"""
    
    def __init__(self, message: str = "Пользователь уже существует"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class InvalidCredentialsError(APEXException):
    """Неверные учетные данные"""
    
    def __init__(self, message: str = "Неверные учетные данные"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class LeadNotFoundError(APEXException):
    """Лид не найден"""
    
    def __init__(self, message: str = "Лид не найден"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class LeadAlreadyExistsError(APEXException):
    """Лид уже существует"""
    
    def __init__(self, message: str = "Лид уже существует"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class ValidationError(APEXException):
    """Ошибка валидации данных"""
    
    def __init__(self, message: str = "Ошибка валидации данных", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class DatabaseError(APEXException):
    """Ошибка базы данных"""
    
    def __init__(self, message: str = "Ошибка базы данных"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExternalServiceError(APEXException):
    """Ошибка внешнего сервиса"""
    
    def __init__(self, message: str = "Ошибка внешнего сервиса", service: Optional[str] = None):
        details = {"service": service} if service else {}
        super().__init__(message, status.HTTP_502_BAD_GATEWAY, details)


class AmoCRMError(ExternalServiceError):
    """Ошибка AmoCRM"""
    
    def __init__(self, message: str = "Ошибка AmoCRM"):
        super().__init__(message, "amocrm")


class NotificationError(APEXException):
    """Ошибка отправки уведомления"""
    
    def __init__(self, message: str = "Ошибка отправки уведомления"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RateLimitError(APEXException):
    """Превышен лимит запросов"""
    
    def __init__(self, message: str = "Превышен лимит запросов"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


class ConfigurationError(APEXException):
    """Ошибка конфигурации"""
    
    def __init__(self, message: str = "Ошибка конфигурации"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_apex_exception(exc: APEXException) -> Dict[str, Any]:
    """Обработка APEX исключений"""
    return {
        "error": {
            "message": exc.message,
            "status_code": exc.status_code,
            "details": exc.details,
            "type": exc.__class__.__name__
        }
    }


def handle_validation_error(exc: ValidationError) -> Dict[str, Any]:
    """Обработка ошибок валидации"""
    return {
        "error": {
            "message": exc.message,
            "status_code": exc.status_code,
            "details": exc.details,
            "type": "ValidationError"
        }
    }


def handle_database_error(exc: DatabaseError) -> Dict[str, Any]:
    """Обработка ошибок базы данных"""
    return {
        "error": {
            "message": "Внутренняя ошибка сервера",
            "status_code": exc.status_code,
            "type": "DatabaseError"
        }
    }


def handle_external_service_error(exc: ExternalServiceError) -> Dict[str, Any]:
    """Обработка ошибок внешних сервисов"""
    return {
        "error": {
            "message": exc.message,
            "status_code": exc.status_code,
            "details": exc.details,
            "type": "ExternalServiceError"
        }
    }
