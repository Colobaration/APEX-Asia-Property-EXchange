#!/usr/bin/env python
"""
Скрипт инициализации данных для админ-панели
"""

import os
import sys
import django
from datetime import datetime, timedelta
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apex_admin.settings')
django.setup()

from django.contrib.auth.models import User
from landings.models import Landing, LandingAnalytics
from integrations.models import APIIntegration, IntegrationLog, WebhookEvent
from analytics.models import Dashboard, Metric, DashboardMetric, Report, ReportExecution, AnalyticsEvent
from logs.models import SystemLog, NotificationTemplate, NotificationLog, SecurityLog


def create_sample_data():
    """Создание тестовых данных"""
    
    print("🚀 Инициализация тестовых данных...")
    
    # Получаем или создаем пользователя
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print("  ✅ Создан пользователь admin")
    
    # 1. Создание лендингов
    print("📄 Создание лендингов...")
    
    landings_data = [
        {
            'name': 'Главная страница',
            'slug': 'main',
            'domain': 'https://apex-asia.com',
            'status': 'active',
            'theme': 'modern',
            'utm_source': 'direct',
            'utm_medium': 'organic',
            'utm_campaign': 'main_page'
        },
        {
            'name': 'Страница продукта',
            'slug': 'product',
            'domain': 'https://apex-asia.com/product',
            'status': 'active',
            'theme': 'professional',
            'utm_source': 'google',
            'utm_medium': 'cpc',
            'utm_campaign': 'product_launch'
        },
        {
            'name': 'Страница документации',
            'slug': 'docs',
            'domain': 'https://apex-asia.com/docs',
            'status': 'active',
            'theme': 'documentation',
            'utm_source': 'organic',
            'utm_medium': 'search',
            'utm_campaign': 'documentation'
        }
    ]
    
    for landing_data in landings_data:
        landing, created = Landing.objects.get_or_create(
            slug=landing_data['slug'],
            defaults={**landing_data, 'created_by': user}
        )
        if created:
            print(f"  ✅ Создан лендинг: {landing.name}")
    
    # 2. Создание API интеграций
    print("🔗 Создание API интеграций...")
    
    integrations_data = [
        {
            'name': 'AmoCRM интеграция',
            'integration_type': 'amocrm',
            'status': 'active',
            'api_key': 'amocrm_key_123',
            'api_secret': 'amocrm_secret_456',
            'webhook_url': 'https://api.apex-asia.com/webhooks/amocrm/',
            'auto_sync': True,
            'sync_interval': 300
        },
        {
            'name': 'WhatsApp уведомления',
            'integration_type': 'whatsapp',
            'status': 'active',
            'api_key': 'whatsapp_key_789',
            'api_secret': 'whatsapp_secret_012',
            'webhook_url': 'https://api.apex-asia.com/webhooks/whatsapp/',
            'auto_sync': True,
            'sync_interval': 60
        },
        {
            'name': 'Telegram Bot',
            'integration_type': 'telegram',
            'status': 'active',
            'api_key': 'telegram_bot_token_345',
            'webhook_url': 'https://api.apex-asia.com/webhooks/telegram/',
            'auto_sync': True,
            'sync_interval': 30
        }
    ]
    
    for integration_data in integrations_data:
        integration, created = APIIntegration.objects.get_or_create(
            name=integration_data['name'],
            defaults={**integration_data, 'created_by': user}
        )
        if created:
            print(f"  ✅ Создана интеграция: {integration.name}")
    
    # 3. Создание дашбордов
    print("📊 Создание дашбордов...")
    
    dashboards_data = [
        {
            'name': 'Общий обзор',
            'description': 'Основные метрики системы',
            'is_public': True,
            'refresh_interval': 300
        },
        {
            'name': 'Аналитика пользователей',
            'description': 'Поведение пользователей',
            'is_public': True,
            'refresh_interval': 600
        },
        {
            'name': 'Мониторинг системы',
            'description': 'Производительность сервисов',
            'is_public': False,
            'refresh_interval': 60
        }
    ]
    
    for dashboard_data in dashboards_data:
        dashboard, created = Dashboard.objects.get_or_create(
            name=dashboard_data['name'],
            defaults={**dashboard_data, 'created_by': user}
        )
        if created:
            print(f"  ✅ Создан дашборд: {dashboard.name}")
    
    # 4. Создание метрик
    print("📈 Создание метрик...")
    
    metrics_data = [
        {
            'name': 'Активные пользователи',
            'description': 'Количество активных пользователей',
            'metric_type': 'counter',
            'data_source': 'users',
            'unit': 'пользователи'
        },
        {
            'name': 'Конверсия',
            'description': 'Процент конверсий',
            'metric_type': 'percentage',
            'data_source': 'landings',
            'unit': '%'
        },
        {
            'name': 'Время отклика API',
            'description': 'Среднее время ответа API',
            'metric_type': 'duration',
            'data_source': 'api',
            'unit': 'мс'
        },
        {
            'name': 'Количество ошибок',
            'description': 'Количество ошибок в системе',
            'metric_type': 'counter',
            'data_source': 'logs',
            'unit': 'ошибки'
        }
    ]
    
    for metric_data in metrics_data:
        metric, created = Metric.objects.get_or_create(
            name=metric_data['name'],
            defaults={**metric_data, 'created_by': user}
        )
        if created:
            print(f"  ✅ Создана метрика: {metric.name}")
    
    # 5. Создание шаблонов уведомлений
    print("📧 Создание шаблонов уведомлений...")
    
    templates_data = [
        {
            'name': 'Новый пользователь',
            'template_type': 'email',
            'subject': 'Добро пожаловать в систему!',
            'content': 'Здравствуйте, {{user_name}}! Добро пожаловать в нашу систему.',
            'is_active': True
        },
        {
            'name': 'Критическая ошибка',
            'template_type': 'telegram',
            'subject': '🚨 Критическая ошибка',
            'content': 'ВНИМАНИЕ! Критическая ошибка в системе: {{error_message}}',
            'is_active': True
        },
        {
            'name': 'Ежедневный отчет',
            'template_type': 'email',
            'subject': '📊 Ежедневный отчет - {{date}}',
            'content': 'Ежедневный отчет системы. Активные пользователи: {{active_users}}',
            'is_active': True
        }
    ]
    
    for template_data in templates_data:
        template, created = NotificationTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults={**template_data, 'created_by': user}
        )
        if created:
            print(f"  ✅ Создан шаблон: {template.name}")
    
    # 6. Создание системных логов
    print("📝 Создание системных логов...")
    
    logs_data = [
        {
            'level': 'INFO',
            'log_type': 'system',
            'source': 'initialization',
            'message': 'Система успешно инициализирована',
            'data': {'status': 'success'}
        },
        {
            'level': 'INFO',
            'log_type': 'integration',
            'source': 'amocrm',
            'message': 'AmoCRM интеграция подключена',
            'data': {'integration': 'amocrm', 'status': 'active'}
        },
        {
            'level': 'WARNING',
            'log_type': 'security',
            'source': 'ssl',
            'message': 'Рекомендуется настроить SSL сертификаты',
            'data': {'priority': 'medium'}
        }
    ]
    
    for log_data in logs_data:
        log = SystemLog.objects.create(**log_data)
        print(f"  ✅ Создан лог: {log.message[:50]}...")
    
    # 7. Создание аналитики лендингов
    print("📊 Создание аналитики лендингов...")
    
    landings = Landing.objects.all()
    for landing in landings:
        # Создаем данные за последние 7 дней
        for i in range(7):
            date = datetime.now().date() - timedelta(days=i)
            analytics, created = LandingAnalytics.objects.get_or_create(
                landing=landing,
                date=date,
                defaults={
                    'visitors': 100 + (i * 20),
                    'unique_visitors': 80 + (i * 15),
                    'conversions': 5 + (i * 2),
                    'leads': 3 + i,
                    'avg_session_duration': 180 + (i * 10),
                    'bounce_rate': 45.0 - (i * 1.5),
                    'organic_traffic': 60,
                    'paid_traffic': 20,
                    'direct_traffic': 15,
                    'referral_traffic': 5
                }
            )
            if created:
                print(f"  ✅ Создана аналитика для {landing.name} на {date}")
    
    # 8. Создание отчетов
    print("📋 Создание отчетов...")
    
    reports_data = [
        {
            'name': 'Ежедневный отчет',
            'description': 'Ежедневный отчет о работе системы',
            'report_type': 'daily',
            'is_scheduled': True,
            'schedule_cron': '0 9 * * *'
        },
        {
            'name': 'Еженедельный отчет',
            'description': 'Еженедельный отчет о пользователях',
            'report_type': 'weekly',
            'is_scheduled': True,
            'schedule_cron': '0 10 * * 1'
        }
    ]
    
    for report_data in reports_data:
        report, created = Report.objects.get_or_create(
            name=report_data['name'],
            defaults={**report_data, 'created_by': user}
        )
        if created:
            print(f"  ✅ Создан отчет: {report.name}")
    
    print("\n🎉 Инициализация данных завершена!")
    print("\n📋 Создано:")
    print(f"  - Лендингов: {Landing.objects.count()}")
    print(f"  - Интеграций: {APIIntegration.objects.count()}")
    print(f"  - Дашбордов: {Dashboard.objects.count()}")
    print(f"  - Метрик: {Metric.objects.count()}")
    print(f"  - Шаблонов уведомлений: {NotificationTemplate.objects.count()}")
    print(f"  - Системных логов: {SystemLog.objects.count()}")
    print(f"  - Аналитики лендингов: {LandingAnalytics.objects.count()}")
    print(f"  - Отчетов: {Report.objects.count()}")
    
    print("\n🚀 Система готова к использованию!")
    print("📊 Админ-панель доступна по адресу: http://localhost:8002/admin/")
    print("👤 Логин: admin / Пароль: admin123")


if __name__ == '__main__':
    create_sample_data()
