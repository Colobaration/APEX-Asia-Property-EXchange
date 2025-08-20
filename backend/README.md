# Asia Deals Backend

Backend API для Asia Deals CRM Integration на FastAPI.

## Структура

```
backend/
├── app/
│   ├── api/           # API endpoints
│   │   ├── leads.py   # Обработка лидов
│   │   ├── auth.py    # OAuth2 аутентификация
│   │   ├── webhooks.py # amoCRM webhooks
│   │   └── analytics.py # Аналитические API
│   ├── core/          # Основные настройки
│   │   ├── config.py  # Конфигурация
│   │   ├── db.py      # База данных
│   │   ├── logging.py # Логирование
│   │   └── utils.py   # Утилиты
│   └── models/        # SQLAlchemy модели
├── tests/             # Тесты
├── Dockerfile         # Docker конфигурация
└── requirements.txt   # Python зависимости
```

## Запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Разработка
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Тесты
pytest

# Миграции
alembic upgrade head
```

## API Endpoints

- `POST /api/leads` - Прием лидов
- `GET /api/auth/amo` - OAuth2 авторизация amoCRM
- `POST /api/webhooks/amo` - Webhooks от amoCRM
- `GET /api/analytics/cpl` - CPL метрики
- `GET /api/analytics/cr` - Conversion Rate
- `GET /api/analytics/roi` - ROI метрики

## Технологии

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- Pytest
