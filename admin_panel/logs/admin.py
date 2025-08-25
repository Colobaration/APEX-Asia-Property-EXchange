from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import SystemLog, NotificationTemplate, NotificationLog, SecurityLog


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'level', 'log_type', 'source', 'message_short', 
        'user', 'ip_address'
    ]
    list_filter = ['level', 'log_type', 'source', 'timestamp', 'user']
    search_fields = ['message', 'source', 'user__username', 'ip_address']
    readonly_fields = [
        'timestamp', 'level', 'log_type', 'source', 'message', 'data',
        'user', 'ip_address', 'user_agent', 'landing', 'integration'
    ]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('timestamp', 'level', 'log_type', 'source')
        }),
        ('Сообщение', {
            'fields': ('message',)
        }),
        ('Контекст', {
            'fields': ('user', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Связи', {
            'fields': ('landing', 'integration'),
            'classes': ('collapse',)
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
    
    def level_display(self, obj):
        """Цветное отображение уровня"""
        colors = {
            'DEBUG': 'gray',
            'INFO': 'blue',
            'WARNING': 'orange',
            'ERROR': 'red',
            'CRITICAL': 'darkred',
        }
        color = colors.get(obj.level, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.level)
    level_display.short_description = 'Уровень'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    actions = ['export_logs', 'clear_old_logs']
    
    def export_logs(self, request, queryset):
        """Экспорт логов"""
        self.message_user(request, f'Экспорт подготовлен для {queryset.count()} логов.')
    export_logs.short_description = 'Экспорт логов'
    
    def clear_old_logs(self, request, queryset):
        """Очистить старые логи"""
        # Удаляем логи старше 30 дней
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=30)
        old_logs = SystemLog.objects.filter(timestamp__lt=cutoff_date)
        count = old_logs.count()
        old_logs.delete()
        self.message_user(request, f'Удалено {count} старых логов.')
    clear_old_logs.short_description = 'Очистить старые логи'


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'template_type', 'is_active', 'created_by', 'created_at'
    ]
    list_filter = ['template_type', 'is_active', 'created_at', 'created_by']
    search_fields = ['name', 'subject', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Содержание', {
            'fields': ('subject', 'content')
        }),
        ('Переменные', {
            'fields': ('variables',),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_template(self, obj):
        """Предварительный просмотр шаблона"""
        return format_html(
            '<a href="#" onclick="previewTemplate({})">Предварительный просмотр</a>',
            obj.id
        )
    preview_template.short_description = 'Предварительный просмотр'
    
    actions = ['activate_templates', 'deactivate_templates']
    
    def activate_templates(self, request, queryset):
        """Активировать шаблоны"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} шаблонов.')
    activate_templates.short_description = 'Активировать шаблоны'
    
    def deactivate_templates(self, request, queryset):
        """Деактивировать шаблоны"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} шаблонов.')
    deactivate_templates.short_description = 'Деактивировать шаблоны'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'template', 'recipient', 'status', 'sent_at', 'created_at'
    ]
    list_filter = ['status', 'template__template_type', 'sent_at', 'created_at']
    search_fields = ['recipient', 'subject', 'template__name']
    readonly_fields = [
        'template', 'recipient', 'subject', 'content', 'status', 
        'sent_at', 'error_message', 'metadata', 'user', 'landing', 
        'integration', 'created_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('template', 'recipient', 'status')
        }),
        ('Содержание', {
            'fields': ('subject', 'content')
        }),
        ('Статус', {
            'fields': ('sent_at', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Контекст', {
            'fields': ('user', 'landing', 'integration'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('metadata', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        """Цветное отображение статуса"""
        colors = {
            'pending': 'orange',
            'sent': 'green',
            'failed': 'red',
            'cancelled': 'gray',
            'delivered': 'blue',
            'read': 'darkgreen',
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_status_display())
    status_display.short_description = 'Статус'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    actions = ['resend_failed_notifications', 'cancel_pending_notifications']
    
    def resend_failed_notifications(self, request, queryset):
        """Повторить отправку неудачных уведомлений"""
        failed_notifications = queryset.filter(status='failed')
        for notification in failed_notifications:
            # Здесь можно добавить логику повторной отправки
            pass
        self.message_user(request, f'Повторная отправка для {failed_notifications.count()} уведомлений.')
    resend_failed_notifications.short_description = 'Повторить отправку неудачных уведомлений'
    
    def cancel_pending_notifications(self, request, queryset):
        """Отменить ожидающие уведомления"""
        pending_notifications = queryset.filter(status='pending')
        updated = pending_notifications.update(status='cancelled')
        self.message_user(request, f'Отменено {updated} ожидающих уведомлений.')
    cancel_pending_notifications.short_description = 'Отменить ожидающие уведомления'


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'event_type', 'user', 'ip_address', 'risk_level'
    ]
    list_filter = ['event_type', 'risk_level', 'timestamp', 'user']
    search_fields = ['user__username', 'ip_address', 'user_agent']
    readonly_fields = [
        'timestamp', 'event_type', 'user', 'ip_address', 'user_agent',
        'details', 'risk_level'
    ]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('timestamp', 'event_type', 'risk_level')
        }),
        ('Пользователь', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Детали', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
    )
    
    def risk_level_display(self, obj):
        """Цветное отображение уровня риска"""
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred',
        }
        color = colors.get(obj.risk_level, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_risk_level_display())
    risk_level_display.short_description = 'Уровень риска'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    actions = ['export_security_logs', 'clear_old_security_logs']
    
    def export_security_logs(self, request, queryset):
        """Экспорт логов безопасности"""
        self.message_user(request, f'Экспорт подготовлен для {queryset.count()} логов безопасности.')
    export_security_logs.short_description = 'Экспорт логов безопасности'
    
    def clear_old_security_logs(self, request, queryset):
        """Очистить старые логи безопасности"""
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=90)
        old_logs = SecurityLog.objects.filter(timestamp__lt=cutoff_date)
        count = old_logs.count()
        old_logs.delete()
        self.message_user(request, f'Удалено {count} старых логов безопасности.')
    clear_old_security_logs.short_description = 'Очистить старые логи безопасности'
