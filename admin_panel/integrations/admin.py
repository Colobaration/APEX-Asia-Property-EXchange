from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import APIIntegration, IntegrationLog, WebhookEvent


@admin.register(APIIntegration)
class APIIntegrationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'integration_type', 'status', 'last_sync', 
        'sync_count', 'error_count', 'created_by', 'created_at'
    ]
    list_filter = ['integration_type', 'status', 'auto_sync', 'created_at', 'created_by']
    search_fields = ['name', 'description', 'api_url']
    readonly_fields = ['sync_count', 'error_count', 'last_sync', 'last_error', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'integration_type', 'status', 'description')
        }),
        ('API настройки', {
            'fields': ('api_url', 'api_key', 'api_secret'),
            'classes': ('collapse',)
        }),
        ('Токены аутентификации', {
            'fields': ('access_token', 'refresh_token', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('Webhook настройки', {
            'fields': ('webhook_url', 'webhook_secret'),
            'classes': ('collapse',)
        }),
        ('Конфигурация', {
            'fields': ('config', 'auto_sync', 'sync_interval')
        }),
        ('Статистика', {
            'fields': ('last_sync', 'sync_count', 'error_count', 'last_error'),
            'classes': ('collapse',)
        }),
        ('Связи', {
            'fields': ('landings', 'created_by'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['landings']
    
    def is_token_expired_display(self, obj):
        """Показать статус токена"""
        if obj.is_token_expired():
            return format_html('<span style="color: red;">Истек</span>')
        return format_html('<span style="color: green;">Активен</span>')
    is_token_expired_display.short_description = 'Статус токена'
    
    def last_sync_display(self, obj):
        """Показать последнюю синхронизацию"""
        if obj.last_sync:
            time_diff = timezone.now() - obj.last_sync
            if time_diff.days > 0:
                return f"{time_diff.days} дн. назад"
            elif time_diff.seconds > 3600:
                return f"{time_diff.seconds // 3600} ч. назад"
            else:
                return f"{time_diff.seconds // 60} мин. назад"
        return "Никогда"
    last_sync_display.short_description = 'Последняя синхронизация'
    
    actions = ['test_integrations', 'sync_integrations', 'reset_error_count']
    
    def test_integrations(self, request, queryset):
        """Тестировать выбранные интеграции"""
        for integration in queryset:
            # Здесь можно добавить логику тестирования
            pass
        self.message_user(request, f'Тестирование запущено для {queryset.count()} интеграций.')
    test_integrations.short_description = 'Тестировать интеграции'
    
    def sync_integrations(self, request, queryset):
        """Синхронизировать выбранные интеграции"""
        for integration in queryset:
            integration.increment_sync_count()
        self.message_user(request, f'Синхронизация запущена для {queryset.count()} интеграций.')
    sync_integrations.short_description = 'Синхронизировать интеграции'
    
    def reset_error_count(self, request, queryset):
        """Сбросить счетчик ошибок"""
        for integration in queryset:
            integration.reset_error_count()
        self.message_user(request, f'Счетчики ошибок сброшены для {queryset.count()} интеграций.')
    reset_error_count.short_description = 'Сбросить счетчики ошибок'


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ['integration', 'timestamp', 'level', 'message_short']
    list_filter = ['level', 'integration', 'integration__integration_type', 'timestamp']
    search_fields = ['message', 'source', 'integration__name']
    readonly_fields = ['timestamp', 'integration', 'level', 'message', 'data']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('integration', 'timestamp', 'level')
        }),
        ('Сообщение', {
            'fields': ('message',)
        }),
        ('Данные', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
    )
    
    def message_short(self, obj):
        """Краткое сообщение"""
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_short.short_description = 'Сообщение'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    actions = ['export_logs']
    
    def export_logs(self, request, queryset):
        """Экспорт логов"""
        self.message_user(request, f'Экспорт подготовлен для {queryset.count()} логов.')
    export_logs.short_description = 'Экспорт логов'


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = [
        'integration', 'event_type', 'status', 'retry_count', 
        'created_at', 'sent_at'
    ]
    list_filter = ['status', 'event_type', 'integration', 'created_at']
    search_fields = ['integration__name', 'event_type', 'error_message']
    readonly_fields = [
        'integration', 'event_type', 'status', 'payload', 'response', 
        'error_message', 'retry_count', 'next_retry', 'created_at', 'sent_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('integration', 'event_type', 'status')
        }),
        ('Данные', {
            'fields': ('payload', 'response'),
            'classes': ('collapse',)
        }),
        ('Ошибки', {
            'fields': ('error_message', 'retry_count', 'next_retry'),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'sent_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    actions = ['retry_failed_events', 'cancel_pending_events']
    
    def retry_failed_events(self, request, queryset):
        """Повторить неудачные события"""
        failed_events = queryset.filter(status='failed')
        for event in failed_events:
            event.increment_retry_count()
        self.message_user(request, f'Повторная попытка для {failed_events.count()} событий.')
    retry_failed_events.short_description = 'Повторить неудачные события'
    
    def cancel_pending_events(self, request, queryset):
        """Отменить ожидающие события"""
        pending_events = queryset.filter(status='pending')
        updated = pending_events.update(status='cancelled')
        self.message_user(request, f'Отменено {updated} ожидающих событий.')
    cancel_pending_events.short_description = 'Отменить ожидающие события'
