from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from landings.models import Landing
from integrations.models import APIIntegration
import json


class SystemLog(models.Model):
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    LOG_TYPES = [
        ('system', 'Система'),
        ('api', 'API'),
        ('landing', 'Лендинг'),
        ('integration', 'Интеграция'),
        ('user', 'Пользователь'),
        ('security', 'Безопасность'),
        ('database', 'База данных'),
        ('email', 'Email'),
        ('webhook', 'Webhook'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Временная метка')
    level = models.CharField(max_length=10, choices=LOG_LEVELS, default='INFO', verbose_name='Уровень')
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, default='system', verbose_name='Тип лога')
    
    source = models.CharField(max_length=100, verbose_name='Источник')
    message = models.TextField(verbose_name='Сообщение')
    data = models.JSONField(default=dict, verbose_name='Данные')
    
    # Контекст
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP адрес')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    
    # Связи
    landing = models.ForeignKey(Landing, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Лендинг')
    integration = models.ForeignKey(APIIntegration, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Интеграция')
    
    class Meta:
        verbose_name = 'Системный лог'
        verbose_name_plural = 'Системные логи'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['level']),
            models.Index(fields=['log_type']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.timestamp} - {self.level} - {self.source}: {self.message[:50]}"
    
    @classmethod
    def log_info(cls, source, message, **kwargs):
        """Создать информационный лог"""
        return cls.objects.create(level='INFO', source=source, message=message, **kwargs)
    
    @classmethod
    def log_warning(cls, source, message, **kwargs):
        """Создать предупреждающий лог"""
        return cls.objects.create(level='WARNING', source=source, message=message, **kwargs)
    
    @classmethod
    def log_error(cls, source, message, **kwargs):
        """Создать лог ошибки"""
        return cls.objects.create(level='ERROR', source=source, message=message, **kwargs)
    
    @classmethod
    def log_critical(cls, source, message, **kwargs):
        """Создать критический лог"""
        return cls.objects.create(level='CRITICAL', source=source, message=message, **kwargs)


class NotificationTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('sms', 'SMS'),
        ('push', 'Push уведомление'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название')
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, verbose_name='Тип шаблона')
    
    subject = models.CharField(max_length=255, blank=True, verbose_name='Тема')
    content = models.TextField(verbose_name='Содержание')
    variables = models.JSONField(default=dict, verbose_name='Переменные')
    
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Создатель')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Шаблон уведомления'
        verbose_name_plural = 'Шаблоны уведомлений'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def render_content(self, context=None):
        """Рендерить содержимое с переменными"""
        if not context:
            context = {}
        
        content = self.content
        for key, value in context.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        
        return content
    
    def render_subject(self, context=None):
        """Рендерить тему с переменными"""
        if not context:
            context = {}
        
        subject = self.subject
        for key, value in context.items():
            subject = subject.replace(f"{{{{{key}}}}}", str(value))
        
        return subject


class NotificationLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('sent', 'Отправлено'),
        ('failed', 'Ошибка'),
        ('cancelled', 'Отменено'),
        ('delivered', 'Доставлено'),
        ('read', 'Прочитано'),
    ]
    
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, verbose_name='Шаблон')
    recipient = models.CharField(max_length=255, verbose_name='Получатель')
    
    subject = models.CharField(max_length=255, blank=True, verbose_name='Тема')
    content = models.TextField(verbose_name='Содержание')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата отправки')
    
    error_message = models.TextField(blank=True, verbose_name='Сообщение об ошибке')
    metadata = models.JSONField(default=dict, verbose_name='Метаданные')
    
    # Контекст
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    landing = models.ForeignKey(Landing, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Лендинг')
    integration = models.ForeignKey(APIIntegration, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Интеграция')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Лог уведомления'
        verbose_name_plural = 'Логи уведомлений'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.template.name} -> {self.recipient} ({self.status})"
    
    def mark_as_sent(self, metadata=None):
        """Отметить как отправленное"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        if metadata:
            self.metadata.update(metadata)
        self.save()
    
    def mark_as_failed(self, error_message=""):
        """Отметить как неудачное"""
        self.status = 'failed'
        self.error_message = error_message
        self.save()
    
    def mark_as_delivered(self):
        """Отметить как доставленное"""
        self.status = 'delivered'
        self.save()
    
    def mark_as_read(self):
        """Отметить как прочитанное"""
        self.status = 'read'
        self.save()


class SecurityLog(models.Model):
    SECURITY_EVENTS = [
        ('login_success', 'Успешный вход'),
        ('login_failed', 'Неудачный вход'),
        ('logout', 'Выход'),
        ('password_change', 'Смена пароля'),
        ('password_reset', 'Сброс пароля'),
        ('account_locked', 'Блокировка аккаунта'),
        ('suspicious_activity', 'Подозрительная активность'),
        ('api_access', 'Доступ к API'),
        ('file_access', 'Доступ к файлу'),
        ('data_export', 'Экспорт данных'),
        ('admin_action', 'Действие администратора'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Временная метка')
    event_type = models.CharField(max_length=30, choices=SECURITY_EVENTS, verbose_name='Тип события')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')
    ip_address = models.GenericIPAddressField(verbose_name='IP адрес')
    user_agent = models.TextField(verbose_name='User Agent')
    
    details = models.JSONField(default=dict, verbose_name='Детали')
    risk_level = models.CharField(max_length=10, choices=[
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('critical', 'Критический'),
    ], default='low', verbose_name='Уровень риска')
    
    class Meta:
        verbose_name = 'Лог безопасности'
        verbose_name_plural = 'Логи безопасности'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['event_type']),
            models.Index(fields=['user']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['risk_level']),
        ]
    
    def __str__(self):
        return f"{self.timestamp} - {self.event_type} - {self.ip_address}"
    
    @classmethod
    def log_login_success(cls, user, ip_address, user_agent, **kwargs):
        """Логировать успешный вход"""
        return cls.objects.create(
            event_type='login_success',
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            risk_level='low',
            **kwargs
        )
    
    @classmethod
    def log_login_failed(cls, username, ip_address, user_agent, **kwargs):
        """Логировать неудачный вход"""
        return cls.objects.create(
            event_type='login_failed',
            ip_address=ip_address,
            user_agent=user_agent,
            details={'username': username},
            risk_level='medium',
            **kwargs
        )
    
    @classmethod
    def log_suspicious_activity(cls, user, ip_address, user_agent, details, **kwargs):
        """Логировать подозрительную активность"""
        return cls.objects.create(
            event_type='suspicious_activity',
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            risk_level='high',
            **kwargs
        )
