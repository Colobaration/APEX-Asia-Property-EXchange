from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Dashboard, Metric, DashboardMetric, Report, ReportExecution, AnalyticsEvent


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'is_public', 'refresh_interval', 'created_by', 'created_at'
    ]
    list_filter = ['is_public', 'created_at', 'created_by']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['shared_with']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description')
        }),
        ('Настройки', {
            'fields': ('layout', 'filters', 'refresh_interval')
        }),
        ('Права доступа', {
            'fields': ('is_public', 'created_by', 'shared_with')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_public', 'make_private']
    
    def make_public(self, request, queryset):
        """Сделать дашборды публичными"""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'Сделано публичными {updated} дашбордов.')
    make_public.short_description = 'Сделать публичными'
    
    def make_private(self, request, queryset):
        """Сделать дашборды приватными"""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'Сделано приватными {updated} дашбордов.')
    make_private.short_description = 'Сделать приватными'


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'metric_type', 'data_source', 'unit', 'color', 'created_by'
    ]
    list_filter = ['metric_type', 'data_source', 'created_at', 'created_by']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'metric_type')
        }),
        ('Источник данных', {
            'fields': ('data_source', 'query', 'config')
        }),
        ('Отображение', {
            'fields': ('unit', 'format_string', 'color')
        }),
        ('Фильтры', {
            'fields': ('filters',),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def color_display(self, obj):
        """Отображение цвета"""
        return format_html(
            '<div style="background-color: {}; width: 20px; height: 20px; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_display.short_description = 'Цвет'


@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = [
        'dashboard', 'metric', 'position_x', 'position_y', 'width', 'height'
    ]
    list_filter = ['dashboard', 'metric__metric_type']
    search_fields = ['dashboard__name', 'metric__name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('dashboard', 'metric')
        }),
        ('Позиция', {
            'fields': ('position_x', 'position_y', 'width', 'height')
        }),
        ('Настройки отображения', {
            'fields': ('title', 'show_title', 'refresh_interval')
        }),
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'report_type', 'is_scheduled', 'export_format', 
        'auto_export', 'created_by', 'created_at'
    ]
    list_filter = ['report_type', 'is_scheduled', 'export_format', 'auto_export', 'created_at', 'created_by']
    search_fields = ['name', 'description']
    readonly_fields = ['last_generated', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'report_type')
        }),
        ('Конфигурация', {
            'fields': ('template', 'config', 'filters')
        }),
        ('Расписание', {
            'fields': ('is_scheduled', 'schedule_cron', 'last_generated'),
            'classes': ('collapse',)
        }),
        ('Экспорт', {
            'fields': ('export_format', 'auto_export', 'export_recipients'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['generate_reports', 'enable_scheduling', 'disable_scheduling']
    
    def generate_reports(self, request, queryset):
        """Генерировать отчеты"""
        for report in queryset:
            # Здесь можно добавить логику генерации отчетов
            pass
        self.message_user(request, f'Генерация запущена для {queryset.count()} отчетов.')
    generate_reports.short_description = 'Генерировать отчеты'
    
    def enable_scheduling(self, request, queryset):
        """Включить расписание"""
        updated = queryset.update(is_scheduled=True)
        self.message_user(request, f'Расписание включено для {updated} отчетов.')
    enable_scheduling.short_description = 'Включить расписание'
    
    def disable_scheduling(self, request, queryset):
        """Отключить расписание"""
        updated = queryset.update(is_scheduled=False)
        self.message_user(request, f'Расписание отключено для {updated} отчетов.')
    disable_scheduling.short_description = 'Отключить расписание'


@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    list_display = [
        'report', 'status', 'triggered_by', 'is_scheduled', 'duration', 'created_at'
    ]
    list_filter = ['status', 'is_scheduled', 'created_at', 'triggered_by']
    search_fields = ['report__name', 'error_message']
    readonly_fields = [
        'report', 'status', 'parameters', 'filters', 'file_path', 'file_size',
        'error_message', 'started_at', 'completed_at', 'duration', 'triggered_by',
        'is_scheduled', 'created_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('report', 'status', 'triggered_by', 'is_scheduled')
        }),
        ('Параметры', {
            'fields': ('parameters', 'filters'),
            'classes': ('collapse',)
        }),
        ('Результат', {
            'fields': ('file_path', 'file_size', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('started_at', 'completed_at', 'duration'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        """Цветное отображение статуса"""
        colors = {
            'pending': 'orange',
            'running': 'blue',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_status_display())
    status_display.short_description = 'Статус'
    
    def duration_display(self, obj):
        """Отображение длительности"""
        if obj.duration > 0:
            if obj.duration < 60:
                return f"{obj.duration:.1f} сек"
            elif obj.duration < 3600:
                return f"{obj.duration / 60:.1f} мин"
            else:
                return f"{obj.duration / 3600:.1f} ч"
        return "-"
    duration_display.short_description = 'Длительность'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    actions = ['retry_failed_executions', 'cancel_pending_executions']
    
    def retry_failed_executions(self, request, queryset):
        """Повторить неудачные выполнения"""
        failed_executions = queryset.filter(status='failed')
        for execution in failed_executions:
            # Здесь можно добавить логику повторного выполнения
            pass
        self.message_user(request, f'Повторное выполнение для {failed_executions.count()} отчетов.')
    retry_failed_executions.short_description = 'Повторить неудачные выполнения'
    
    def cancel_pending_executions(self, request, queryset):
        """Отменить ожидающие выполнения"""
        pending_executions = queryset.filter(status='pending')
        updated = pending_executions.update(status='cancelled')
        self.message_user(request, f'Отменено {updated} ожидающих выполнений.')
    cancel_pending_executions.short_description = 'Отменить ожидающие выполнения'


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = [
        'landing', 'event_type', 'value', 'session_id', 'timestamp'
    ]
    list_filter = ['event_type', 'landing', 'device_type', 'timestamp']
    search_fields = ['landing__name', 'session_id', 'user_id', 'ip_address']
    readonly_fields = [
        'landing', 'event_type', 'event_data', 'value', 'session_id', 'user_id',
        'ip_address', 'country', 'city', 'user_agent', 'device_type', 'browser', 'os',
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('landing', 'event_type', 'value', 'timestamp')
        }),
        ('Сессия', {
            'fields': ('session_id', 'user_id'),
            'classes': ('collapse',)
        }),
        ('География', {
            'fields': ('ip_address', 'country', 'city'),
            'classes': ('collapse',)
        }),
        ('Устройство', {
            'fields': ('user_agent', 'device_type', 'browser', 'os'),
            'classes': ('collapse',)
        }),
        ('UTM данные', {
            'fields': ('utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'),
            'classes': ('collapse',)
        }),
        ('Данные события', {
            'fields': ('event_data',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    actions = ['export_events', 'clear_old_events']
    
    def export_events(self, request, queryset):
        """Экспорт событий"""
        self.message_user(request, f'Экспорт подготовлен для {queryset.count()} событий.')
    export_events.short_description = 'Экспорт событий'
    
    def clear_old_events(self, request, queryset):
        """Очистить старые события"""
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=90)
        old_events = AnalyticsEvent.objects.filter(timestamp__lt=cutoff_date)
        count = old_events.count()
        old_events.delete()
        self.message_user(request, f'Удалено {count} старых событий.')
    clear_old_events.short_description = 'Очистить старые события'
