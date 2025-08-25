from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from landings.models import Landing
from integrations.models import APIIntegration
import json


class Dashboard(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    # Настройки дашборда
    layout = models.JSONField(default=dict, verbose_name='Макет')
    filters = models.JSONField(default=dict, verbose_name='Фильтры')
    refresh_interval = models.IntegerField(default=300, verbose_name='Интервал обновления (сек)')
    
    # Права доступа
    is_public = models.BooleanField(default=False, verbose_name='Публичный')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Создатель')
    shared_with = models.ManyToManyField(User, related_name='shared_dashboards', blank=True, verbose_name='Поделено с')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Дашборд'
        verbose_name_plural = 'Дашборды'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Metric(models.Model):
    METRIC_TYPES = [
        ('counter', 'Счетчик'),
        ('gauge', 'Индикатор'),
        ('histogram', 'Гистограмма'),
        ('line_chart', 'Линейный график'),
        ('bar_chart', 'Столбчатый график'),
        ('pie_chart', 'Круговая диаграмма'),
        ('table', 'Таблица'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES, verbose_name='Тип метрики')
    
    # Источник данных
    data_source = models.CharField(max_length=100, verbose_name='Источник данных')
    query = models.TextField(blank=True, verbose_name='Запрос')
    config = models.JSONField(default=dict, verbose_name='Конфигурация')
    
    # Отображение
    unit = models.CharField(max_length=20, blank=True, verbose_name='Единица измерения')
    format_string = models.CharField(max_length=50, blank=True, verbose_name='Формат отображения')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет')
    
    # Фильтры
    filters = models.JSONField(default=dict, verbose_name='Фильтры')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Создатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Метрика'
        verbose_name_plural = 'Метрики'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DashboardMetric(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='metrics', verbose_name='Дашборд')
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, verbose_name='Метрика')
    
    # Позиция на дашборде
    position_x = models.IntegerField(default=0, verbose_name='Позиция X')
    position_y = models.IntegerField(default=0, verbose_name='Позиция Y')
    width = models.IntegerField(default=6, verbose_name='Ширина')
    height = models.IntegerField(default=4, verbose_name='Высота')
    
    # Настройки отображения
    title = models.CharField(max_length=200, blank=True, verbose_name='Заголовок')
    show_title = models.BooleanField(default=True, verbose_name='Показывать заголовок')
    refresh_interval = models.IntegerField(default=0, verbose_name='Интервал обновления (сек)')
    
    class Meta:
        verbose_name = 'Метрика дашборда'
        verbose_name_plural = 'Метрики дашборда'
        unique_together = ['dashboard', 'metric']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.metric.name}"


class Report(models.Model):
    REPORT_TYPES = [
        ('daily', 'Ежедневный'),
        ('weekly', 'Еженедельный'),
        ('monthly', 'Ежемесячный'),
        ('quarterly', 'Ежеквартальный'),
        ('yearly', 'Ежегодный'),
        ('custom', 'Пользовательский'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('html', 'HTML'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name='Тип отчета')
    
    # Конфигурация
    template = models.TextField(blank=True, verbose_name='Шаблон')
    config = models.JSONField(default=dict, verbose_name='Конфигурация')
    filters = models.JSONField(default=dict, verbose_name='Фильтры')
    
    # Расписание
    is_scheduled = models.BooleanField(default=False, verbose_name='По расписанию')
    schedule_cron = models.CharField(max_length=100, blank=True, verbose_name='Cron выражение')
    last_generated = models.DateTimeField(null=True, blank=True, verbose_name='Последняя генерация')
    
    # Экспорт
    export_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf', verbose_name='Формат экспорта')
    auto_export = models.BooleanField(default=False, verbose_name='Автоэкспорт')
    export_recipients = models.JSONField(default=list, verbose_name='Получатели экспорта')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Создатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ReportExecution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('running', 'Выполняется'),
        ('completed', 'Завершен'),
        ('failed', 'Ошибка'),
        ('cancelled', 'Отменен'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='executions', verbose_name='Отчет')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    
    # Параметры выполнения
    parameters = models.JSONField(default=dict, verbose_name='Параметры')
    filters = models.JSONField(default=dict, verbose_name='Фильтры')
    
    # Результат
    file_path = models.CharField(max_length=500, blank=True, verbose_name='Путь к файлу')
    file_size = models.BigIntegerField(default=0, verbose_name='Размер файла')
    error_message = models.TextField(blank=True, verbose_name='Сообщение об ошибке')
    
    # Временные метки
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Начало выполнения')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Завершение выполнения')
    duration = models.FloatField(default=0, verbose_name='Длительность (сек)')
    
    # Контекст
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Запустил')
    is_scheduled = models.BooleanField(default=False, verbose_name='По расписанию')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Выполнение отчета'
        verbose_name_plural = 'Выполнения отчетов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report.name} - {self.created_at}"
    
    def start_execution(self):
        """Начать выполнение"""
        self.status = 'running'
        self.started_at = timezone.now()
        self.save()
    
    def complete_execution(self, file_path=None, file_size=0):
        """Завершить выполнение"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if self.started_at:
            self.duration = (self.completed_at - self.started_at).total_seconds()
        if file_path:
            self.file_path = file_path
        self.file_size = file_size
        self.save()
    
    def fail_execution(self, error_message=""):
        """Завершить с ошибкой"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        if self.started_at:
            self.duration = (self.completed_at - self.started_at).total_seconds()
        self.error_message = error_message
        self.save()


class AnalyticsEvent(models.Model):
    EVENT_TYPES = [
        ('page_view', 'Просмотр страницы'),
        ('form_submit', 'Отправка формы'),
        ('button_click', 'Клик по кнопке'),
        ('link_click', 'Клик по ссылке'),
        ('scroll', 'Прокрутка'),
        ('time_on_page', 'Время на странице'),
        ('bounce', 'Отказ'),
        ('conversion', 'Конверсия'),
        ('custom', 'Пользовательское событие'),
    ]
    
    landing = models.ForeignKey(Landing, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Лендинг')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name='Тип события')
    
    # Данные события
    event_data = models.JSONField(default=dict, verbose_name='Данные события')
    value = models.FloatField(default=0, verbose_name='Значение')
    
    # Сессия
    session_id = models.CharField(max_length=100, blank=True, verbose_name='ID сессии')
    user_id = models.CharField(max_length=100, blank=True, verbose_name='ID пользователя')
    
    # География
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP адрес')
    country = models.CharField(max_length=2, blank=True, verbose_name='Страна')
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    
    # Устройство
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    device_type = models.CharField(max_length=20, blank=True, verbose_name='Тип устройства')
    browser = models.CharField(max_length=50, blank=True, verbose_name='Браузер')
    os = models.CharField(max_length=50, blank=True, verbose_name='Операционная система')
    
    # UTM данные
    utm_source = models.CharField(max_length=100, blank=True, verbose_name='UTM Source')
    utm_medium = models.CharField(max_length=100, blank=True, verbose_name='UTM Medium')
    utm_campaign = models.CharField(max_length=100, blank=True, verbose_name='UTM Campaign')
    utm_term = models.CharField(max_length=100, blank=True, verbose_name='UTM Term')
    utm_content = models.CharField(max_length=100, blank=True, verbose_name='UTM Content')
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Временная метка')
    
    class Meta:
        verbose_name = 'Событие аналитики'
        verbose_name_plural = 'События аналитики'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['event_type']),
            models.Index(fields=['landing']),
            models.Index(fields=['session_id']),
            models.Index(fields=['utm_source']),
            models.Index(fields=['utm_medium']),
            models.Index(fields=['utm_campaign']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"
    
    @classmethod
    def track_page_view(cls, landing, session_id, user_id="", **kwargs):
        """Отследить просмотр страницы"""
        return cls.objects.create(
            event_type='page_view',
            landing=landing,
            session_id=session_id,
            user_id=user_id,
            **kwargs
        )
    
    @classmethod
    def track_conversion(cls, landing, session_id, user_id="", value=0, **kwargs):
        """Отследить конверсию"""
        return cls.objects.create(
            event_type='conversion',
            landing=landing,
            session_id=session_id,
            user_id=user_id,
            value=value,
            **kwargs
        )
