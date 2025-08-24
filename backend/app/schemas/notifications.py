"""
Pydantic схемы для уведомлений
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Типы уведомлений"""
    EMAIL = "email"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    SMS = "sms"


class NotificationStatus(str, Enum):
    """Статусы уведомлений"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"


class NotificationPriority(str, Enum):
    """Приоритеты уведомлений"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationBase(BaseModel):
    """Базовая схема уведомления"""
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    recipient_telegram_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    """Схема для создания уведомления"""
    pass


class NotificationUpdate(BaseModel):
    """Схема для обновления уведомления"""
    title: Optional[str] = None
    message: Optional[str] = None
    status: Optional[NotificationStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(NotificationBase):
    """Схема ответа с данными уведомления"""
    id: int
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Схема для списка уведомлений с пагинацией"""
    notifications: List[NotificationResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class NotificationFilter(BaseModel):
    """Схема для фильтрации уведомлений"""
    notification_type: Optional[NotificationType] = None
    status: Optional[NotificationStatus] = None
    priority: Optional[NotificationPriority] = None
    recipient_email: Optional[EmailStr] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class NotificationTemplate(BaseModel):
    """Шаблон уведомления"""
    name: str
    title_template: str
    message_template: str
    notification_type: NotificationType
    variables: List[str]
    is_active: bool = True


class NotificationStatistics(BaseModel):
    """Статистика уведомлений"""
    total_sent: int
    total_delivered: int
    total_failed: int
    delivery_rate: float
    avg_delivery_time: Optional[float] = None
    notifications_by_type: Dict[str, int]
    notifications_by_status: Dict[str, int]
