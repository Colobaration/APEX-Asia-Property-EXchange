from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from landings.models import Landing
import json


class APIIntegration(models.Model):
    INTEGRATION_TYPES = [
        ('amocrm', 'AmoCRM'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('payment', 'Payment'),
        ('analytics', 'Analytics'),
        ('crm', 'CRM'),
        ('webhook', 'Webhook'),
        ('api', 'Custom API'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('inactive', 'Неактивна'),
        ('error', 'Ошибка'),
        ('testing', 'Тестирование'),
        ('maintenance', 'Обслуживание'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название')
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPES, verbose_name='Тип интеграции')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive', verbose_name='Статус')
    
    # API настройки
    api_url = models.URLField(blank=True, verbose_name='API URL')
    api_key = models.CharField(max_length=255, blank=True, verbose_name='API Key')
    api_secret = models.CharField(max_length=255, blank=True, verbose_name='API Secret')
    
    # Токены аутентификации
    access_token = models.TextField(blank=True, verbose_name='Access Token')
    refresh_token = models.TextField(blank=True, verbose_name='Refresh Token')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Истекает в')
    
    # Webhook настройки
    webhook_url = models.URLField(blank=True, verbose_name='Webhook URL')
    webhook_secret = models.CharField(max_length=255, blank=True, verbose_name='Webhook Secret')
    
    # Конфигурация
    config = models.JSONField(default=dict, verbose_name='Конфигурация')
    auto_sync = models.BooleanField(default=False, verbose_name='Автосинхронизация')
    sync_interval = models.IntegerField(default=3600, verbose_name='Интервал синхронизации (сек)')
    
    # Статистика
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name='Последняя синхронизация')
    sync_count = models.IntegerField(default=0, verbose_name='Количество синхронизаций')
    error_count = models.IntegerField(default=0, verbose_name='Количество ошибок')
    last_error = models.TextField(blank=True, verbose_name='Последняя ошибка')
    
    # Связи
    landings = models.ManyToManyField(Landing, blank=True, verbose_name='Лендинги')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Создатель')
    
    # Метаданные
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'API интеграция'
        verbose_name_plural = 'API интеграции'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_integration_type_display()})"
    
    def is_token_expired(self):
        """Проверить, истек ли токен"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def get_config_value(self, key, default=None):
        """Получить значение из конфигурации"""
        return self.config.get(key, default)
    
    def set_config_value(self, key, value):
        """Установить значение в конфигурации"""
        self.config[key] = value
        self.save()
    
    def increment_sync_count(self):
        """Увеличить счетчик синхронизаций"""
        self.sync_count += 1
        self.last_sync = timezone.now()
        self.save()
    
    def increment_error_count(self, error_message=""):
        """Увеличить счетчик ошибок"""
        self.error_count += 1
        self.last_error = error_message
        self.status = 'error'
        self.save()
    
    def reset_error_count(self):
        """Сбросить счетчик ошибок"""
        self.error_count = 0
        self.last_error = ""
        if self.status == 'error':
            self.status = 'active'
        self.save()


class IntegrationLog(models.Model):
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    integration = models.ForeignKey(APIIntegration, on_delete=models.CASCADE, related_name='logs', verbose_name='Интеграция')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Временная метка')
    level = models.CharField(max_length=10, choices=LOG_LEVELS, default='INFO', verbose_name='Уровень')
    message = models.TextField(verbose_name='Сообщение')
    data = models.JSONField(default=dict, verbose_name='Данные')
    
    class Meta:
        verbose_name = 'Лог интеграции'
        verbose_name_plural = 'Логи интеграций'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.integration.name} - {self.timestamp} - {self.level}"


class WebhookEvent(models.Model):
    EVENT_TYPES = [
        ('lead_created', 'Создан лид'),
        ('lead_updated', 'Обновлен лид'),
        ('deal_created', 'Создана сделка'),
        ('deal_updated', 'Обновлена сделка'),
        ('contact_created', 'Создан контакт'),
        ('contact_updated', 'Обновлен контакт'),
        ('form_submitted', 'Отправлена форма'),
        ('payment_received', 'Получен платеж'),
        ('custom', 'Пользовательское событие'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('sent', 'Отправлено'),
        ('failed', 'Ошибка'),
        ('retry', 'Повторная попытка'),
    ]
    
    integration = models.ForeignKey(APIIntegration, on_delete=models.CASCADE, related_name='webhook_events', verbose_name='Интеграция')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name='Тип события')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    
    payload = models.JSONField(default=dict, verbose_name='Данные события')
    response = models.JSONField(default=dict, verbose_name='Ответ')
    error_message = models.TextField(blank=True, verbose_name='Сообщение об ошибке')
    
    retry_count = models.IntegerField(default=0, verbose_name='Количество попыток')
    next_retry = models.DateTimeField(null=True, blank=True, verbose_name='Следующая попытка')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата отправки')
    
    class Meta:
        verbose_name = 'Webhook событие'
        verbose_name_plural = 'Webhook события'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.integration.name} - {self.event_type} - {self.status}"
    
    def mark_as_sent(self, response_data=None):
        """Отметить как отправленное"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        if response_data:
            self.response = response_data
        self.save()
    
    def mark_as_failed(self, error_message=""):
        """Отметить как неудачное"""
        self.status = 'failed'
        self.error_message = error_message
        self.save()
    
    def increment_retry_count(self):
        """Увеличить счетчик попыток"""
        self.retry_count += 1
        self.status = 'retry'
        self.save()
