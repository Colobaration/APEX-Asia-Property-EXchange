from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Landing, LandingAnalytics


@admin.register(Landing)
class LandingAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'slug', 'status', 'theme', 'visitors_today', 
        'conversions_today', 'conversion_rate', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'theme', 'created_at', 'created_by']
    search_fields = ['name', 'slug', 'domain', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['visitors_today', 'visitors_total', 'conversions_today', 'conversions_total', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'domain', 'status', 'description')
        }),
        ('Дизайн', {
            'fields': ('theme', 'config')
        }),
        ('UTM метки', {
            'fields': ('utm_source', 'utm_medium', 'utm_campaign'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('visitors_today', 'visitors_total', 'conversions_today', 'conversions_total'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def conversion_rate(self, obj):
        """Конверсионная ставка"""
        if obj.visitors_today > 0:
            rate = (obj.conversions_today / obj.visitors_today) * 100
            return f"{rate:.1f}%"
        return "0%"
    conversion_rate.short_description = 'Конверсия сегодня'
    
    def get_full_url_display(self, obj):
        """Полный URL с UTM метками"""
        return format_html('<a href="{}" target="_blank">{}</a>', obj.get_full_url(), obj.get_full_url())
    get_full_url_display.short_description = 'Полный URL'
    
    actions = ['activate_landings', 'deactivate_landings', 'reset_statistics']
    
    def activate_landings(self, request, queryset):
        """Активировать выбранные лендинги"""
        updated = queryset.update(status='active')
        self.message_user(request, f'Активировано {updated} лендингов.')
    activate_landings.short_description = 'Активировать выбранные лендинги'
    
    def deactivate_landings(self, request, queryset):
        """Деактивировать выбранные лендинги"""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'Деактивировано {updated} лендингов.')
    deactivate_landings.short_description = 'Деактивировать выбранные лендинги'
    
    def reset_statistics(self, request, queryset):
        """Сбросить статистику"""
        for landing in queryset:
            landing.visitors_today = 0
            landing.conversions_today = 0
            landing.save()
        self.message_user(request, f'Статистика сброшена для {queryset.count()} лендингов.')
    reset_statistics.short_description = 'Сбросить статистику'


@admin.register(LandingAnalytics)
class LandingAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'landing', 'date', 'visitors', 'unique_visitors', 'conversions', 
        'conversion_rate', 'avg_session_duration', 'bounce_rate'
    ]
    list_filter = ['date', 'landing', 'landing__status']
    search_fields = ['landing__name']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('landing', 'date')
        }),
        ('Основные метрики', {
            'fields': ('visitors', 'unique_visitors', 'page_views', 'conversions', 'leads')
        }),
        ('Поведенческие метрики', {
            'fields': ('avg_session_duration', 'bounce_rate')
        }),
        ('Источники трафика', {
            'fields': ('organic_traffic', 'paid_traffic', 'direct_traffic', 'referral_traffic'),
            'classes': ('collapse',)
        }),
        ('UTM данные', {
            'fields': ('utm_data',),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def conversion_rate(self, obj):
        """Конверсионная ставка"""
        return f"{obj.get_conversion_rate():.1f}%"
    conversion_rate.short_description = 'Конверсия'
    
    def avg_session_duration_display(self, obj):
        """Длительность сессии в читаемом формате"""
        minutes = int(obj.avg_session_duration // 60)
        seconds = int(obj.avg_session_duration % 60)
        return f"{minutes}:{seconds:02d}"
    avg_session_duration_display.short_description = 'Длительность сессии'
    
    actions = ['export_analytics']
    
    def export_analytics(self, request, queryset):
        """Экспорт аналитики"""
        # Здесь можно добавить логику экспорта
        self.message_user(request, f'Экспорт подготовлен для {queryset.count()} записей.')
    export_analytics.short_description = 'Экспорт аналитики'
