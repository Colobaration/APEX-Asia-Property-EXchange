from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.core.db import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # ID пользователя (если уведомление для конкретного пользователя)
    type = Column(String(50), nullable=False)  # Тип уведомления: email, telegram, whatsapp, push
    status = Column(String(20), default="pending")  # Статус: pending, sent, failed, delivered
    recipient = Column(String(255), nullable=False)  # Получатель (email, phone, chat_id)
    subject = Column(String(255), nullable=True)  # Тема (для email)
    message = Column(Text, nullable=False)  # Текст сообщения
    template_name = Column(String(100), nullable=True)  # Название шаблона
    template_data = Column(JSON, nullable=True)  # Данные для шаблона
    priority = Column(String(20), default="normal")  # Приоритет: low, normal, high, urgent
    scheduled_at = Column(DateTime(timezone=True), nullable=True)  # Время отправки (для отложенных)
    sent_at = Column(DateTime(timezone=True), nullable=True)  # Время фактической отправки
    retry_count = Column(Integer, default=0)  # Количество попыток отправки
    max_retries = Column(Integer, default=3)  # Максимальное количество попыток
    error_message = Column(Text, nullable=True)  # Сообщение об ошибке
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Дополнительные поля
    source = Column(String(50), nullable=True)  # Источник уведомления: system, user, webhook
    source_id = Column(String(100), nullable=True)  # ID источника
    meta_data = Column(JSON, nullable=True)  # Дополнительные метаданные
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type}', status='{self.status}', recipient='{self.recipient}')>"
    
    @property
    def is_sent(self):
        """Проверяет, отправлено ли уведомление"""
        return self.status in ["sent", "delivered"]
    
    @property
    def is_failed(self):
        """Проверяет, не удалось ли отправить уведомление"""
        return self.status == "failed" and self.retry_count >= self.max_retries
    
    @property
    def can_retry(self):
        """Проверяет, можно ли повторить отправку"""
        return self.status in ["failed", "pending"] and self.retry_count < self.max_retries
    
    def increment_retry(self):
        """Увеличивает счетчик попыток"""
        self.retry_count += 1
        if self.retry_count >= self.max_retries:
            self.status = "failed"
    
    def mark_sent(self, sent_at=None):
        """Отмечает уведомление как отправленное"""
        self.status = "sent"
        self.sent_at = sent_at or func.now()
    
    def mark_delivered(self):
        """Отмечает уведомление как доставленное"""
        self.status = "delivered"
    
    def mark_failed(self, error_message=None):
        """Отмечает уведомление как неудачное"""
        self.status = "failed"
        if error_message:
            self.error_message = error_message
