#!/usr/bin/env python
"""
Скрипт инициализации универсальных данных по best practices для любой технической системы
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


def create_universal_best_practices_data():
    """Создание универсальных данных по best practices для любой технической системы"""
    
    print("🚀 Инициализация универсальных данных по best practices...")
    
    # 1. Создание лендингов по best practices
    print("📄 Создание лендингов...")
    
    landings_data = [
        {
            'name': 'Главная страница системы',
            'slug': 'main',
            'domain': 'apex-asia.com',
            'status': 'active',
            'configuration': {
                'theme': 'modern',
                'cta_button': 'Начать работу',
                'hero_section': True,
                'features_section': True,
                'contact_form': True,
                'pricing_section': True
            },
            'utm_source': 'direct',
            'utm_medium': 'organic',
            'utm_campaign': 'main_page'
        },
        {
            'name': 'Страница продукта',
            'slug': 'product',
            'domain': 'apex-asia.com',
            'status': 'active',
            'configuration': {
                'theme': 'professional',
                'cta_button': 'Попробовать бесплатно',
                'product_demo': True,
                'testimonials': True,
                'pricing_table': True,
                'faq_section': True
            },
            'utm_source': 'google',
            'utm_medium': 'cpc',
            'utm_campaign': 'product_launch'
        },
        {
            'name': 'Страница документации',
            'slug': 'docs',
            'domain': 'apex-asia.com',
            'status': 'active',
            'configuration': {
                'theme': 'documentation',
                'cta_button': 'Получить поддержку',
                'search_functionality': True,
                'code_examples': True,
                'api_reference': True,
                'tutorials': True
            },
            'utm_source': 'organic',
            'utm_medium': 'search',
            'utm_campaign': 'documentation'
        },
        {
            'name': 'Страница контактов',
            'slug': 'contact',
            'domain': 'apex-asia.com',
            'status': 'active',
            'configuration': {
                'theme': 'contact',
                'cta_button': 'Отправить сообщение',
                'contact_form': True,
                'office_locations': True,
                'support_channels': True,
                'social_links': True
            },
            'utm_source': 'direct',
            'utm_medium': 'organic',
            'utm_campaign': 'contact_page'
        }
    ]
    
    for landing_data in landings_data:
        landing, created = Landing.objects.get_or_create(
            slug=landing_data['slug'],
            defaults=landing_data
        )
        if created:
            print(f"  ✅ Создан лендинг: {landing.name}")
    
    # 2. Создание API интеграций по best practices
    print("🔗 Создание API интеграций...")
    
    integrations_data = [
        {
            'name': 'Основная CRM система',
            'integration_type': 'amocrm',
            'api_key': 'crm_prod_key_123',
            'api_secret': 'crm_prod_secret_456',
            'webhook_url': 'https://api.apex-asia.com/webhooks/crm/',
            'status': 'active',
            'sync_frequency': 300,  # 5 минут
            'last_sync': datetime.now() - timedelta(hours=1)
        },
        {
            'name': 'Система уведомлений',
            'integration_type': 'whatsapp',
            'api_key': 'notifications_key_789',
            'api_secret': 'notifications_secret_012',
            'webhook_url': 'https://api.apex-asia.com/webhooks/notifications/',
            'status': 'active',
            'sync_frequency': 60,  # 1 минута
            'last_sync': datetime.now() - timedelta(minutes=30)
        },
        {
            'name': 'Telegram Bot для мониторинга',
            'integration_type': 'telegram',
            'api_key': 'telegram_bot_token_345',
            'api_secret': '',
            'webhook_url': 'https://api.apex-asia.com/webhooks/telegram/',
            'status': 'active',
            'sync_frequency': 30,  # 30 секунд
            'last_sync': datetime.now() - timedelta(minutes=15)
        },
        {
            'name': 'Email сервис',
            'integration_type': 'email',
            'api_key': 'smtp_username',
            'api_secret': 'smtp_password',
            'webhook_url': '',
            'status': 'active',
            'sync_frequency': 0,  # По требованию
            'last_sync': datetime.now() - timedelta(hours=2)
        },
        {
            'name': 'Система аналитики',
            'integration_type': 'analytics',
            'api_key': 'analytics_key_567',
            'api_secret': 'analytics_secret_890',
            'webhook_url': 'https://api.apex-asia.com/webhooks/analytics/',
            'status': 'active',
            'sync_frequency': 600,  # 10 минут
            'last_sync': datetime.now() - timedelta(minutes=45)
        },
        {
            'name': 'Система платежей',
            'integration_type': 'payment',
            'api_key': 'payment_key_123',
            'api_secret': 'payment_secret_456',
            'webhook_url': 'https://api.apex-asia.com/webhooks/payments/',
            'status': 'active',
            'sync_frequency': 120,  # 2 минуты
            'last_sync': datetime.now() - timedelta(minutes=20)
        }
    ]
    
    for integration_data in integrations_data:
        integration, created = APIIntegration.objects.get_or_create(
            name=integration_data['name'],
            defaults=integration_data
        )
        if created:
            print(f"  ✅ Создана интеграция: {integration.name}")
    
    # 3. Создание дашбордов по best practices
    print("📊 Создание дашбордов...")
    
    dashboards_data = [
        {
            'name': 'Общий обзор системы',
            'description': 'Основные метрики и статус системы',
            'is_public': True,
            'refresh_interval': 300
        },
        {
            'name': 'Аналитика пользователей',
            'description': 'Поведение пользователей и конверсии',
            'is_public': True,
            'refresh_interval': 600
        },
        {
            'name': 'Мониторинг системы',
            'description': 'Производительность и статус сервисов',
            'is_public': False,
            'refresh_interval': 60
        },
        {
            'name': 'Бизнес метрики',
            'description': 'Ключевые бизнес показатели',
            'is_public': True,
            'refresh_interval': 1800
        },
        {
            'name': 'Техническая аналитика',
            'description': 'Производительность API и базы данных',
            'is_public': False,
            'refresh_interval': 120
        }
    ]
    
    for dashboard_data in dashboards_data:
        dashboard, created = Dashboard.objects.get_or_create(
            name=dashboard_data['name'],
            defaults=dashboard_data
        )
        if created:
            print(f"  ✅ Создан дашборд: {dashboard.name}")
    
    # 4. Создание метрик по best practices
    print("📈 Создание метрик...")
    
    metrics_data = [
        {
            'name': 'Активные пользователи',
            'description': 'Количество активных пользователей в системе',
            'metric_type': 'counter',
            'unit': 'пользователи',
            'calculation_method': 'sum'
        },
        {
            'name': 'Конверсия регистраций',
            'description': 'Процент посетителей, которые зарегистрировались',
            'metric_type': 'percentage',
            'unit': '%',
            'calculation_method': 'average'
        },
        {
            'name': 'Время отклика API',
            'description': 'Среднее время ответа API',
            'metric_type': 'duration',
            'unit': 'мс',
            'calculation_method': 'average'
        },
        {
            'name': 'Количество ошибок',
            'description': 'Количество ошибок в системе',
            'metric_type': 'counter',
            'unit': 'ошибки',
            'calculation_method': 'sum'
        },
        {
            'name': 'Использование ресурсов',
            'description': 'Использование CPU и памяти',
            'metric_type': 'percentage',
            'unit': '%',
            'calculation_method': 'average'
        },
        {
            'name': 'Трафик на сайт',
            'description': 'Количество посещений сайта',
            'metric_type': 'counter',
            'unit': 'посещения',
            'calculation_method': 'sum'
        },
        {
            'name': 'Успешные транзакции',
            'description': 'Количество успешных транзакций',
            'metric_type': 'counter',
            'unit': 'транзакции',
            'calculation_method': 'sum'
        },
        {
            'name': 'Время работы системы',
            'description': 'Uptime системы',
            'metric_type': 'percentage',
            'unit': '%',
            'calculation_method': 'average'
        }
    ]
    
    for metric_data in metrics_data:
        metric, created = Metric.objects.get_or_create(
            name=metric_data['name'],
            defaults=metric_data
        )
        if created:
            print(f"  ✅ Создана метрика: {metric.name}")
    
    # 5. Создание шаблонов уведомлений по best practices
    print("📧 Создание шаблонов уведомлений...")
    
    templates_data = [
        {
            'name': 'Новый пользователь',
            'notification_type': 'email',
            'subject': 'Новый пользователь зарегистрировался',
            'content': '''
Здравствуйте!

Новый пользователь зарегистрировался в системе:
- Email: {{ user_email }}
- Имя: {{ user_name }}
- Источник: {{ source }}
- Время: {{ registration_time }}

С уважением,
Система мониторинга
            ''',
            'is_active': True
        },
        {
            'name': 'Критическая ошибка',
            'notification_type': 'telegram',
            'subject': '🚨 Критическая ошибка в системе',
            'content': '''
ВНИМАНИЕ! Критическая ошибка в системе:

Компонент: {{ component }}
Ошибка: {{ error_message }}
Время: {{ timestamp }}
Сервер: {{ server_name }}

Требуется немедленное вмешательство!
            ''',
            'is_active': True
        },
        {
            'name': 'Ежедневный отчет',
            'notification_type': 'email',
            'subject': '📊 Ежедневный отчет системы - {{ date }}',
            'content': '''
Ежедневный отчет системы

📈 Основные метрики:
- Активные пользователи: {{ active_users }}
- Новые регистрации: {{ new_registrations }}
- Трафик: {{ traffic_count }}
- Ошибки: {{ errors_count }}
- Uptime: {{ uptime }}%

🔗 Интеграции:
- CRM: {{ crm_status }}
- Уведомления: {{ notifications_status }}
- Платежи: {{ payments_status }}

С уважением,
Система мониторинга
            ''',
            'is_active': True
        },
        {
            'name': 'Предупреждение о ресурсах',
            'notification_type': 'telegram',
            'subject': '⚠️ Высокое использование ресурсов',
            'content': '''
Предупреждение о ресурсах:

Сервер: {{ server_name }}
CPU: {{ cpu_usage }}%
Память: {{ memory_usage }}%
Диск: {{ disk_usage }}%

Рекомендуется проверить нагрузку.
            ''',
            'is_active': True
        },
        {
            'name': 'Успешная интеграция',
            'notification_type': 'email',
            'subject': '✅ Интеграция восстановлена',
            'content': '''
Интеграция восстановлена:

Сервис: {{ service_name }}
Время восстановления: {{ recovery_time }}
Статус: {{ status }}

Система работает нормально.
            ''',
            'is_active': True
        }
    ]
    
    for template_data in templates_data:
        template, created = NotificationTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        if created:
            print(f"  ✅ Создан шаблон: {template.name}")
    
    # 6. Создание системных логов по best practices
    print("📝 Создание системных логов...")
    
    logs_data = [
        {
            'level': 'INFO',
            'message': 'Система успешно инициализирована',
            'log_type': 'system',
            'context': {'component': 'initialization', 'status': 'success'}
        },
        {
            'level': 'INFO',
            'message': 'Все интеграции подключены и работают',
            'log_type': 'integration',
            'context': {'integrations_count': 6, 'status': 'active'}
        },
        {
            'level': 'WARNING',
            'message': 'Рекомендуется настроить SSL сертификаты',
            'log_type': 'security',
            'context': {'component': 'ssl', 'priority': 'medium'}
        },
        {
            'level': 'INFO',
            'message': 'База данных синхронизирована',
            'log_type': 'database',
            'context': {'component': 'database', 'status': 'synced'}
        },
        {
            'level': 'INFO',
            'message': 'Кэш очищен и оптимизирован',
            'log_type': 'performance',
            'context': {'component': 'cache', 'action': 'optimized'}
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
                    'visitors': 150 + (i * 25),
                    'conversions': 8 + (i * 3),
                    'session_duration': 200 + (i * 15),
                    'bounce_rate': 40.0 - (i * 1.5),
                    'traffic_source': json.dumps({
                        'organic': 55,
                        'direct': 30,
                        'social': 10,
                        'paid': 5
                    })
                }
            )
            if created:
                print(f"  ✅ Создана аналитика для {landing.name} на {date}")
    
    # 8. Создание отчетов
    print("📋 Создание отчетов...")
    
    reports_data = [
        {
            'name': 'Ежедневный отчет системы',
            'description': 'Ежедневный отчет о работе системы',
            'report_type': 'daily',
            'schedule': '0 9 * * *',  # Каждый день в 9:00
            'is_active': True
        },
        {
            'name': 'Еженедельный отчет пользователей',
            'description': 'Еженедельный отчет о пользователях',
            'report_type': 'weekly',
            'schedule': '0 10 * * 1',  # Каждый понедельник в 10:00
            'is_active': True
        },
        {
            'name': 'Месячный отчет производительности',
            'description': 'Месячный отчет о производительности системы',
            'report_type': 'monthly',
            'schedule': '0 11 1 * *',  # Первого числа каждого месяца в 11:00
            'is_active': True
        }
    ]
    
    for report_data in reports_data:
        report, created = Report.objects.get_or_create(
            name=report_data['name'],
            defaults=report_data
        )
        if created:
            print(f"  ✅ Создан отчет: {report.name}")
    
    print("\n🎉 Инициализация универсальных данных по best practices завершена!")
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
    create_universal_best_practices_data()
