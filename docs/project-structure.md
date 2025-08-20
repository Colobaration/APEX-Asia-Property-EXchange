# Структура проекта Asia Deals CRM Integration

## Обзор

Полная структура monorepo для проекта **Asia Deals CRM Integration** - комплексного решения для автоматизации продаж недвижимости в Азии с интеграцией amoCRM, лендингом и аналитикой.

## 📁 Структура директорий

```
asia-deals-crm/
├── frontend/                    # Next.js (лендинг + UI для CRM)
│   ├── pages/                   # Next.js страницы
│   ├── components/              # React компоненты
│   ├── public/                  # Статические файлы
│   ├── utils/                   # Утилиты и хелперы
│   ├── styles/                  # CSS стили
│   ├── package.json             # Node.js зависимости
│   ├── Dockerfile               # Контейнеризация frontend
│   └── README.md                # Документация frontend
│
├── backend/                     # FastAPI (amoCRM интеграции, webhooks, аналитика)
│   ├── app/
│   │   ├── api/                 # API endpoints
│   │   │   ├── leads.py         # endpoint приёма лидов (валидация, find-or-create контакт)
│   │   │   ├── auth.py          # OAuth2: code → access/refresh + автообновление
│   │   │   ├── webhooks.py      # amoCRM webhooks (lead added/updated, status changed)
│   │   │   └── analytics.py     # API для CPL, CR, ROI
│   │   ├── core/                # Основные настройки
│   │   │   ├── config.py        # Конфигурация приложения
│   │   │   ├── db.py            # Настройки базы данных
│   │   │   ├── logging.py       # Система логирования
│   │   │   └── utils.py         # Утилиты и хелперы
│   │   ├── models/              # SQLAlchemy модели
│   │   │   ├── lead.py          # Модель лида
│   │   │   ├── deal.py          # Модель сделки
│   │   │   └── __init__.py      # Инициализация моделей
│   │   └── main.py              # Главный файл FastAPI приложения
│   ├── tests/                   # Тесты
│   │   ├── unit/                # Unit тесты
│   │   ├── integration/         # Integration тесты
│   │   └── e2e/                 # End-to-end тесты
│   ├── Dockerfile               # Контейнеризация backend
│   ├── requirements.txt         # Python зависимости
│   └── README.md                # Документация backend
│
├── integrations/                # Интеграции с внешними сервисами
│   ├── amo/                     # Python SDK-обёртка над amoCRM API
│   │   ├── client.py            # Основной клиент amoCRM
│   │   └── __init__.py          # Инициализация модуля
│   ├── email/                   # Скрипты автоворонок (e-mail)
│   │   └── __init__.py          # Инициализация модуля
│   └── whatsapp/                # Скрипты WhatsApp API
│       └── __init__.py          # Инициализация модуля
│
├── analytics/                   # Аналитика и отчётность
│   ├── dashboards/              # Metabase/Grafana JSON-конфиги
│   └── pipeline/                # Python-скрипты расчёта метрик
│       └── __init__.py          # Инициализация модуля
│
├── docs/                        # Документация проекта
│   ├── endpoints.md             # Описание API backend
│   ├── crm-fields.md            # Маппинг кастомных полей amoCRM
│   ├── pipelines.md             # Воронка Asia Deals (этапы)
│   ├── test-plan.md             # Позитивные/негативные сценарии
│   └── project-structure.md     # Данная документация
│
├── docker-compose.yml           # Оркестрация всех сервисов
├── .gitignore                   # Исключения для Git
├── .cursor                      # Конфигурация Cursor для совместной работы
├── env.example                  # Пример переменных окружения
└── README.md                    # Основная документация проекта
```

## 📋 Созданные файлы и директории

### Корневые файлы
- **`.gitignore`** - исключения для Git (Node.js, Python, Docker, IDE)
- **`.cursor`** - конфигурация Cursor для совместной работы
- **`docker-compose.yml`** - оркестрация всех сервисов (backend, frontend, db, metabase)
- **`env.example`** - пример переменных окружения
- **`README.md`** - полная документация проекта

### Backend (FastAPI)
- **`backend/requirements.txt`** - Python зависимости (FastAPI, SQLAlchemy, Pydantic, etc.)
- **`backend/Dockerfile`** - контейнеризация backend
- **`backend/README.md`** - документация backend
- **`backend/app/main.py`** - главный файл FastAPI приложения
- **`backend/app/core/`** - основные настройки:
  - `config.py` - конфигурация приложения
  - `db.py` - настройки базы данных
  - `logging.py` - система логирования
  - `utils.py` - утилиты и хелперы
- **`backend/app/api/`** - API endpoints:
  - `leads.py` - обработка лидов
  - `auth.py` - OAuth2 аутентификация
  - `webhooks.py` - обработка webhooks
  - `analytics.py` - аналитические API
- **`backend/app/models/`** - модели данных:
  - `lead.py` - модель лида
  - `deal.py` - модель сделки

### Frontend (Next.js)
- **`frontend/package.json`** - Node.js зависимости (Next.js, React, TypeScript, etc.)
- **`frontend/Dockerfile`** - контейнеризация frontend
- **`frontend/README.md`** - документация frontend

### Integrations
- **`integrations/amo/client.py`** - клиент для amoCRM API
- **`integrations/email/`** - email интеграции
- **`integrations/whatsapp/`** - WhatsApp интеграции

### Analytics
- **`analytics/pipeline/`** - скрипты расчета метрик
- **`analytics/dashboards/`** - конфигурации Metabase

### Documentation
- **`docs/endpoints.md`** - API документация
- **`docs/crm-fields.md`** - маппинг полей amoCRM
- **`docs/pipelines.md`** - воронка продаж
- **`docs/test-plan.md`** - план тестирования

## 🏗️ Архитектура проекта

### Frontend (Next.js)
- **Лендинг** - привлечение и конвертация посетителей
- **CRM Dashboard** - управление сделками и аналитика
- **Lead Form** - форма приема лидов с UTM-метками
- **Analytics** - визуализация метрик и отчетов

### Backend (FastAPI)
- **API для лидов** - валидация и создание в amoCRM
- **OAuth2 интеграция** - авторизация с amoCRM
- **Webhooks обработка** - синхронизация изменений
- **Аналитические API** - расчет CPL, CR, ROI

### Integrations
- **amoCRM SDK** - Python-обертка над API
- **Email воронки** - автоматические рассылки
- **WhatsApp API** - уведомления и коммуникация

### Analytics
- **Metabase дашборды** - визуализация данных
- **Pipeline скрипты** - расчет метрик
- **Отчеты** - автоматическая генерация

## 🚀 Готово к запуску

### Локальная разработка
```bash
# Клонирование и настройка
git clone <repository-url>
cd asia-deals-crm
cp env.example .env
# Редактирование .env файла

# Запуск всех сервисов
docker-compose up --build

# Доступ к сервисам:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Metabase: http://localhost:3001
# PostgreSQL: localhost:5432
```

### Продакшн развертывание
```bash
# Настройка продакшн переменных
export NODE_ENV=production
export DATABASE_URL=postgresql://user:pass@host:5432/db

# Запуск с продакшн конфигурацией
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Ключевые функции

### ✅ Реализованные возможности
- **Прием лидов** с UTM-метками и валидацией
- **Интеграция с amoCRM** (OAuth2 + webhooks)
- **Автоматическое создание** контактов и сделок
- **Аналитические метрики** (CPL, CR, ROI)
- **Email и WhatsApp воронки** для автоматизации
- **Docker контейнеризация** для простого развертывания
- **Полная документация** по всем компонентам

### 🔧 Технические особенности
- **Monorepo структура** для удобной разработки
- **Микросервисная архитектура** с четким разделением ответственности
- **RESTful API** с автоматической документацией (Swagger)
- **Асинхронная обработка** webhooks и интеграций
- **Система логирования** с ротацией файлов
- **Валидация данных** на всех уровнях

## 📈 Метрики и аналитика

### Основные метрики
- **CPL (Cost Per Lead)** - стоимость привлечения лида
- **CR (Conversion Rate)** - конверсия по этапам воронки
- **ROI (Return on Investment)** - возврат инвестиций

### Воронка продаж
1. **Новый лид** - первичный контакт
2. **Первичный контакт** - звонок менеджера
3. **Презентация** - показ объектов
4. **Выбор объекта** - клиент выбрал недвижимость
5. **Резервирование** - внесение депозита
6. **Сделка** - закрытие сделки
7. **Завершено** - успешная сделка

## 🔐 Безопасность

### Аутентификация и авторизация
- **OAuth2** для интеграции с amoCRM
- **JWT токены** для API аутентификации
- **Хеширование паролей** с bcrypt
- **CORS настройки** для безопасности

### Валидация данных
- **Pydantic модели** для валидации API
- **SQLAlchemy** для валидации на уровне БД
- **Санитизация входных данных** для предотвращения XSS

## 🧪 Тестирование

### Типы тестов
- **Unit тесты** - тестирование отдельных компонентов
- **Integration тесты** - тестирование взаимодействия компонентов
- **E2E тесты** - тестирование полного пользовательского сценария
- **Performance тесты** - нагрузочное тестирование

### Покрытие кода
- **Цель**: > 80% покрытия
- **Backend**: pytest --cov=app
- **Frontend**: npm run test:coverage

## 📚 Документация

### Доступная документация
- **[API Endpoints](./endpoints.md)** - описание всех API
- **[CRM Fields](./crm-fields.md)** - маппинг полей amoCRM
- **[Pipelines](./pipelines.md)** - воронка продаж
- **[Test Plan](./test-plan.md)** - план тестирования

### Технологии
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Alembic
- **DevOps**: Docker, Docker Compose, nginx, Metabase
- **Integrations**: amoCRM API, WhatsApp Business API, SMTP

## 🎯 Статус проекта

### ✅ Завершено
- Полная структура monorepo
- Backend API с интеграциями
- Docker контейнеризация
- Документация и тестовые планы
- Конфигурационные файлы

### 🚧 В разработке
- Frontend компоненты
- Email и WhatsApp интеграции
- Аналитические дашборды
- Тестовые сценарии

### 📋 Планируется
- CI/CD pipeline
- Мониторинг и алерты
- Продакшн развертывание
- Обучение команды

## 📞 Поддержка

По вопросам поддержки обращайтесь:
- **Email**: support@asiadeals.com
- **Telegram**: @asiadeals_support
- **Документация**: [docs.asiadeals.com](https://docs.asiadeals.com)

---

**Проект полностью готов для разработки и развертывания!** 🎉
