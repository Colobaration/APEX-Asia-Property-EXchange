"""
Сервис для работы с уведомлениями
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, desc, asc

from app.models.notification import Notification
from app.schemas.notifications import (
    NotificationCreate,
    NotificationUpdate,
    NotificationFilter,
    NotificationStatistics
)
from app.core.exceptions import (
    NotificationError,
    ValidationError,
    DatabaseError
)
from app.integrations.email.client import EmailClient
from app.integrations.telegram.client import TelegramClient
from app.integrations.whatsapp.client import WhatsAppClient


class NotificationService:
    """Сервис для работы с уведомлениями"""

    def __init__(self, db: Session):
        self.db = db
        self.email_client = EmailClient()
        self.telegram_client = TelegramClient()
        self.whatsapp_client = WhatsAppClient()

    def get_notification_by_id(self, notification_id: int) -> Optional[Notification]:
        """Получение уведомления по ID"""
        return self.db.query(Notification).filter(Notification.id == notification_id).first()

    def get_notifications(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[NotificationFilter] = None
    ) -> List[Notification]:
        """Получение списка уведомлений с фильтрацией"""
        query = self.db.query(Notification)

        if filters:
            # Фильтр по типу уведомления
            if filters.notification_type:
                query = query.filter(Notification.notification_type == filters.notification_type)

            # Фильтр по статусу
            if filters.status:
                query = query.filter(Notification.status == filters.status)

            # Фильтр по приоритету
            if filters.priority:
                query = query.filter(Notification.priority == filters.priority)

            # Фильтр по получателю
            if filters.recipient_email:
                query = query.filter(Notification.recipient_email == filters.recipient_email)

            # Фильтр по дате создания
            if filters.created_after:
                query = query.filter(Notification.created_at >= filters.created_after)

            if filters.created_before:
                query = query.filter(Notification.created_at <= filters.created_before)

        # Сортировка по дате создания (новые сначала)
        query = query.order_by(desc(Notification.created_at))

        return query.offset(skip).limit(limit).all()

    def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """Создание нового уведомления"""
        db_notification = Notification(
            title=notification_data.title,
            message=notification_data.message,
            notification_type=notification_data.notification_type,
            priority=notification_data.priority,
            recipient_email=notification_data.recipient_email,
            recipient_phone=notification_data.recipient_phone,
            recipient_telegram_id=notification_data.recipient_telegram_id,
            metadata=notification_data.metadata
        )

        try:
            self.db.add(db_notification)
            self.db.commit()
            self.db.refresh(db_notification)
            return db_notification
        except IntegrityError:
            self.db.rollback()
            raise DatabaseError("Ошибка при создании уведомления")

    def update_notification(self, notification_id: int, notification_data: NotificationUpdate) -> Notification:
        """Обновление уведомления"""
        notification = self.get_notification_by_id(notification_id)
        if not notification:
            raise NotificationError(f"Уведомление с ID {notification_id} не найдено")

        # Обновляем только переданные поля
        update_data = notification_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(notification, field, value)

        try:
            self.db.commit()
            self.db.refresh(notification)
            return notification
        except IntegrityError:
            self.db.rollback()
            raise DatabaseError("Ошибка при обновлении уведомления")

    def delete_notification(self, notification_id: int) -> bool:
        """Удаление уведомления"""
        notification = self.get_notification_by_id(notification_id)
        if not notification:
            raise NotificationError(f"Уведомление с ID {notification_id} не найдено")

        self.db.delete(notification)
        self.db.commit()
        return True

    def mark_as_read(self, notification_id: int) -> Notification:
        """Отметить уведомление как прочитанное"""
        notification = self.get_notification_by_id(notification_id)
        if not notification:
            raise NotificationError(f"Уведомление с ID {notification_id} не найдено")

        notification.status = "read"
        notification.read_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(notification)
        return notification

    def send_notification(self, notification_id: int) -> bool:
        """Отправка уведомления"""
        notification = self.get_notification_by_id(notification_id)
        if not notification:
            raise NotificationError(f"Уведомление с ID {notification_id} не найдено")

        try:
            success = False

            if notification.notification_type == "email" and notification.recipient_email:
                success = self._send_email_notification(notification)
            elif notification.notification_type == "telegram" and notification.recipient_telegram_id:
                success = self._send_telegram_notification(notification)
            elif notification.notification_type == "whatsapp" and notification.recipient_phone:
                success = self._send_whatsapp_notification(notification)
            else:
                raise NotificationError(f"Неподдерживаемый тип уведомления: {notification.notification_type}")

            if success:
                notification.status = "sent"
                notification.sent_at = datetime.utcnow()
            else:
                notification.status = "failed"
                notification.error_message = "Ошибка отправки"

            self.db.commit()
            return success

        except Exception as e:
            notification.status = "failed"
            notification.error_message = str(e)
            self.db.commit()
            raise NotificationError(f"Ошибка отправки уведомления: {str(e)}")

    def _send_email_notification(self, notification: Notification) -> bool:
        """Отправка email уведомления"""
        try:
            return self.email_client.send_email(
                to_email=notification.recipient_email,
                subject=notification.title,
                message=notification.message
            )
        except Exception as e:
            raise NotificationError(f"Ошибка отправки email: {str(e)}")

    def _send_telegram_notification(self, notification: Notification) -> bool:
        """Отправка Telegram уведомления"""
        try:
            return self.telegram_client.send_message(
                chat_id=notification.recipient_telegram_id,
                message=f"{notification.title}\n\n{notification.message}"
            )
        except Exception as e:
            raise NotificationError(f"Ошибка отправки Telegram: {str(e)}")

    def _send_whatsapp_notification(self, notification: Notification) -> bool:
        """Отправка WhatsApp уведомления"""
        try:
            return self.whatsapp_client.send_message(
                phone=notification.recipient_phone,
                message=f"{notification.title}\n\n{notification.message}"
            )
        except Exception as e:
            raise NotificationError(f"Ошибка отправки WhatsApp: {str(e)}")

    def get_notification_statistics(self) -> NotificationStatistics:
        """Получение статистики уведомлений"""
        total_sent = self.db.query(Notification).filter(Notification.status == "sent").count()
        total_delivered = self.db.query(Notification).filter(Notification.status == "delivered").count()
        total_failed = self.db.query(Notification).filter(Notification.status == "failed").count()
        total_notifications = self.db.query(Notification).count()

        delivery_rate = (total_delivered / total_notifications * 100) if total_notifications > 0 else 0

        # Статистика по типам уведомлений
        notifications_by_type = {}
        types = self.db.query(Notification.notification_type).distinct().all()
        for notification_type in types:
            type_count = self.db.query(Notification).filter(
                Notification.notification_type == notification_type[0]
            ).count()
            notifications_by_type[notification_type[0]] = type_count

        # Статистика по статусам
        notifications_by_status = {}
        statuses = self.db.query(Notification.status).distinct().all()
        for status in statuses:
            status_count = self.db.query(Notification).filter(
                Notification.status == status[0]
            ).count()
            notifications_by_status[status[0]] = status_count

        return NotificationStatistics(
            total_sent=total_sent,
            total_delivered=total_delivered,
            total_failed=total_failed,
            delivery_rate=delivery_rate,
            notifications_by_type=notifications_by_type,
            notifications_by_status=notifications_by_status
        )

    def get_pending_notifications(self, limit: int = 50) -> List[Notification]:
        """Получение ожидающих отправки уведомлений"""
        return (
            self.db.query(Notification)
            .filter(Notification.status == "pending")
            .order_by(asc(Notification.created_at))
            .limit(limit)
            .all()
        )

    def retry_failed_notifications(self, max_retries: int = 3) -> List[bool]:
        """Повторная отправка неудачных уведомлений"""
        failed_notifications = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.status == "failed",
                    Notification.retry_count < max_retries
                )
            )
            .all()
        )

        results = []
        for notification in failed_notifications:
            notification.retry_count += 1
            notification.status = "pending"
            
            try:
                success = self.send_notification(notification.id)
                results.append(success)
            except Exception:
                results.append(False)

        self.db.commit()
        return results

    def create_bulk_notifications(self, notifications_data: List[NotificationCreate]) -> List[Notification]:
        """Создание множественных уведомлений"""
        notifications = []
        
        for notification_data in notifications_data:
            notification = self.create_notification(notification_data)
            notifications.append(notification)

        return notifications

    def send_bulk_notifications(self, notification_ids: List[int]) -> Dict[int, bool]:
        """Отправка множественных уведомлений"""
        results = {}
        
        for notification_id in notification_ids:
            try:
                success = self.send_notification(notification_id)
                results[notification_id] = success
            except Exception:
                results[notification_id] = False

        return results
