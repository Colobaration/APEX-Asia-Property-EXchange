# APEX Asia Property Exchange - API Server

Полноценный API сервер для системы управления недвижимостью в Азии с интеграцией amoCRM.

## 🚀 Быстрый запуск

### 1. Запуск через скрипт (рекомендуется)
```bash
# Запустить API сервер
./scripts/start-api.sh

# Остановить сервисы
./scripts/start-api.sh stop

# Перезапустить сервисы
./scripts/start-api.sh restart

# Показать логи
./scripts/start-api.sh logs

# Показать статус
./scripts/start-api.sh status
```

### 2. Ручной запуск через Docker Compose
```bash
# Запуск staging окружения
docker-compose -f docker-compose.staging.yml up -d

# Просмотр логов
docker-compose -f docker-compose.staging.yml logs -f

# Остановка
docker-compose -f docker-compose.staging.yml down
```

## 🌐 API Endpoints

### Основные endpoints:
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Root**: http://localhost:8001/

### API Endpoints:
- **Webhooks**: http://localhost:8001/api/webhooks
- **Auth**: http://localhost:8001/api/auth
- **Leads**: http://localhost:8001/api/leads
- **Analytics**: http://localhost:8001/api/analytics
- **Notifications**: http://localhost:8001/api/notifications

## 🗄️ Сервисы

- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6380
- **Nginx**: localhost:80 (прокси)

## ⚙️ Конфигурация

### Переменные окружения
Все настройки находятся в файле `.env.staging`:

```bash
# Основные настройки
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# amoCRM интеграция
AMOCRM_CLIENT_ID=your_client_id
AMOCRM_CLIENT_SECRET=your_client_secret
AMOCRM_DOMAIN=your_domain.amocrm.ru

# База данных
DB_URL=postgresql://asia:asia@db:5432/asia_crm_staging
DB_USER=asia
DB_PASSWORD=asia
DB_NAME=asia_crm_staging

# Redis
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=your_redis_password

# Безопасность
SECRET_KEY=your-staging-secret-key
JWT_SECRET=your-staging-jwt-secret

# Email, WhatsApp, Telegram настройки
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

WHATSAPP_API_URL=https://api.whatsapp.com
WHATSAPP_API_KEY=your_whatsapp_key

TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_DEFAULT_CHAT_ID=your_chat_id
```

## 🔧 Разработка

### Структура проекта
```
backend/
├── app/
│   ├── api/           # API роутеры
│   ├── core/          # Основные настройки
│   ├── integrations/  # Интеграции (amoCRM, email, etc.)
│   ├── models/        # Модели данных
│   └── main.py        # Точка входа
├── alembic/           # Миграции БД
└── requirements.txt   # Зависимости
```

### Добавление нового API endpoint
1. Создайте новый файл в `backend/app/api/`
2. Определите роутер с FastAPI
3. Подключите в `backend/app/main.py`

### Логирование
Логи сохраняются в `backend/logs/` и выводятся в консоль.
Уровень логирования настраивается через `LOG_LEVEL` в `.env.staging`.

## 🐛 Отладка

### Просмотр логов
```bash
# Все сервисы
docker-compose -f docker-compose.staging.yml logs -f

# Только backend
docker-compose -f docker-compose.staging.yml logs -f backend

# Только база данных
docker-compose -f docker-compose.staging.yml logs -f db
```

### Проверка статуса сервисов
```bash
# Статус контейнеров
docker-compose -f docker-compose.staging.yml ps

# Health check API
curl http://localhost:8001/health

# Проверка базы данных
docker-compose -f docker-compose.staging.yml exec db pg_isready -U asia

# Проверка Redis
docker-compose -f docker-compose.staging.yml exec redis redis-cli ping
```

## 🔒 Безопасность

- CORS настроен для staging доменов
- Trusted Host middleware включен в production
- JWT токены для аутентификации
- Переменные окружения для секретов

## 📊 Мониторинг

- Health check endpoint для Kubernetes
- Логирование всех запросов
- Метрики (если включены)
- Автоматические health checks для всех сервисов

## 🚀 Production

Для production окружения:
1. Создайте `.env.production`
2. Обновите `docker-compose.production.yml`
3. Настройте SSL/TLS
4. Включите мониторинг и алерты
