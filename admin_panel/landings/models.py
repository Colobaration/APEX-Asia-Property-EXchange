from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import URLValidator
import json


class Landing(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('inactive', 'Неактивен'),
        ('maintenance', 'Техобслуживание'),
        ('draft', 'Черновик'),
    ]
    
    THEME_CHOICES = [
        ('default', 'Стандартная'),
        ('modern', 'Современная'),
        ('minimal', 'Минималистичная'),
        ('corporate', 'Корпоративная'),
        ('creative', 'Креативная'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    domain = models.CharField(max_length=255, validators=[URLValidator()], verbose_name='Домен')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    
    # Конфигурация
    config = models.JSONField(default=dict, verbose_name='Конфигурация')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='default', verbose_name='Тема')
    
    # UTM метки
    utm_source = models.CharField(max_length=100, blank=True, verbose_name='UTM Source')
    utm_medium = models.CharField(max_length=100, blank=True, verbose_name='UTM Medium')
    utm_campaign = models.CharField(max_length=100, blank=True, verbose_name='UTM Campaign')
    
    # Статистика
    visitors_today = models.IntegerField(default=0, verbose_name='Посетители сегодня')
    visitors_total = models.IntegerField(default=0, verbose_name='Всего посетителей')
    conversions_today = models.IntegerField(default=0, verbose_name='Конверсии сегодня')
    conversions_total = models.IntegerField(default=0, verbose_name='Всего конверсий')
    
    # Метаданные
    description = models.TextField(blank=True, verbose_name='Описание')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Создатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Лендинг'
        verbose_name_plural = 'Лендинги'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_full_url(self):
        """Получить полный URL лендинга с UTM метками"""
        url = self.domain
        utm_params = []
        
        if self.utm_source:
            utm_params.append(f"utm_source={self.utm_source}")
        if self.utm_medium:
            utm_params.append(f"utm_medium={self.utm_medium}")
        if self.utm_campaign:
            utm_params.append(f"utm_campaign={self.utm_campaign}")
        
        if utm_params:
            url += "?" + "&".join(utm_params)
        
        return url
    
    def get_config_value(self, key, default=None):
        """Получить значение из конфигурации"""
        return self.config.get(key, default)
    
    def set_config_value(self, key, value):
        """Установить значение в конфигурации"""
        self.config[key] = value
        self.save()


class LandingAnalytics(models.Model):
    landing = models.ForeignKey(Landing, on_delete=models.CASCADE, related_name='analytics', verbose_name='Лендинг')
    date = models.DateField(verbose_name='Дата')
    
    # Основные метрики
    visitors = models.IntegerField(default=0, verbose_name='Посетители')
    unique_visitors = models.IntegerField(default=0, verbose_name='Уникальные посетители')
    page_views = models.IntegerField(default=0, verbose_name='Просмотры страниц')
    conversions = models.IntegerField(default=0, verbose_name='Конверсии')
    leads = models.IntegerField(default=0, verbose_name='Лиды')
    
    # Поведенческие метрики
    avg_session_duration = models.FloatField(default=0, verbose_name='Средняя длительность сессии')
    bounce_rate = models.FloatField(default=0, verbose_name='Процент отказов')
    
    # Источники трафика
    organic_traffic = models.IntegerField(default=0, verbose_name='Органический трафик')
    paid_traffic = models.IntegerField(default=0, verbose_name='Платный трафик')
    direct_traffic = models.IntegerField(default=0, verbose_name='Прямой трафик')
    referral_traffic = models.IntegerField(default=0, verbose_name='Реферальный трафик')
    
    # UTM данные
    utm_data = models.JSONField(default=dict, verbose_name='UTM данные')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Аналитика лендинга'
        verbose_name_plural = 'Аналитика лендингов'
        unique_together = ['landing', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.landing.name} - {self.date}"
    
    def get_conversion_rate(self):
        """Получить конверсионную ставку"""
        if self.visitors > 0:
            return (self.conversions / self.visitors) * 100
        return 0
    
    def get_utm_source_stats(self):
        """Получить статистику по UTM источникам"""
        return self.utm_data.get('sources', {})
