# 🔗 Настройка вебхук сервера AmoCRM

## 📋 Обзор

Вебхук сервер для AmoCRM позволяет получать real-time уведомления об изменениях в лидах и контактах. Это обеспечивает автоматическую синхронизацию данных между amoCRM и нашей системой.

## 🏗️ Архитектура

```
┌─────────────┐    HTTP POST    ┌─────────────────┐    Database    ┌─────────────┐
│   amoCRM    │ ──────────────► │  Webhook Server │ ─────────────► │ PostgreSQL  │
│             │                 │                 │                │             │
│  - Leads    │                 │  - Validation   │                │  - Leads    │
│  - Contacts │                 │  - Processing   │                │  - Contacts │
│  - Events   │                 │  - Logging      │                │  - Tokens   │
└─────────────┘                 └─────────────────┘                └─────────────┘
```

## 🔧 Настройка

### 1. Конфигурация переменных окружения

Добавьте в `.env` файл:

```bash
# amoCRM Webhook Configuration
AMOCRM_CLIENT_ID=your_client_id
AMOCRM_CLIENT_SECRET=your_client_secret
AMOCRM_DOMAIN=your-company.amocrm.ru
AMOCRM_REDIRECT_URI=http://localhost:8000/api/auth/amo/callback

# Database
DB_URL=postgresql://asia:asia@db:5432/asia_crm

# Security
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# Logging
LOG_LEVEL=INFO
```

### 2. Настройка webhook в amoCRM

1. **Войдите в amoCRM** под администратором
2. **Перейдите в Настройки** → **Интеграции** → **Webhooks**
3. **Добавьте новый webhook:**

```
URL: http://your-domain.com/api/webhooks/amo
События:
✅ Создание лидов
✅ Изменение лидов
✅ Удаление лидов
✅ Создание контактов
✅ Изменение контактов
```

### 3. Настройка кастомных полей

Создайте в amoCRM кастомные поля с указанными ID:

#### Для лидов:
| Поле | ID | Тип | Описание |
|------|----|-----|----------|
| UTM Source | 123458 | Текст | Источник трафика |
| UTM Medium | 123459 | Текст | Канал трафика |
| UTM Campaign | 123460 | Текст | Название кампании |
| UTM Content | 123461 | Текст | Контент |
| UTM Term | 123462 | Текст | Ключевые слова |
| Стоимость объекта | 123463 | Число | Стоимость недвижимости |
| Комиссия | 123464 | Число | Комиссия агента |

#### Для контактов:
| Поле | ID | Тип | Описание |
|------|----|-----|----------|
| Телефон | 123456 | Телефон | Основной телефон |
| Email | 123457 | Email | Основной email |

## 🚀 Запуск сервера

### Локальный запуск

```bash
# Установка зависимостей
cd backend
pip install -r requirements.txt

# Запуск сервера
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker запуск

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f backend
```

## 📡 API Endpoints

### Основной webhook endpoint

```
POST /api/webhooks/amo
```

**Headers:**
- `X-Client-UUID` - UUID клиента amoCRM
- `X-Signature` - HMAC подпись
- `X-Account-ID` - ID аккаунта amoCRM
- `Content-Type: application/json`

**Body:**
```json
{
  "leads": {
    "add": [
      {
        "id": 12345,
        "name": "Новый лид",
        "status_id": 1,
        "created_at": 1640995200,
        "custom_fields_values": [
          {
            "field_id": 123458,
            "values": [{"value": "google"}]
          }
        ]
      }
    ],
    "update": [],
    "delete": []
  },
  "contacts": {
    "add": [],
    "update": []
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Processed 1 events",
  "events_processed": 1,
  "timestamp": "2024-01-01T12:00:00Z",
  "errors": null
}
```

### Тестовые endpoints

#### Health check
```
GET /api/webhooks/amo/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "database": "connected",
  "webhook_endpoint": "active"
}
```

#### Test endpoint
```
GET /api/webhooks/amo/test
```

**Response:**
```json
{
  "status": "success",
  "message": "Webhook endpoint is working",
  "timestamp": "2024-01-01T12:00:00Z",
  "endpoint": "/api/webhooks/amo",
  "supported_events": [
    "leads.add",
    "leads.update",
    "leads.delete",
    "contacts.add",
    "contacts.update"
  ]
}
```

## 🧪 Тестирование

### Автоматические тесты

```bash
# Запуск unit тестов
cd backend
pytest tests/unit/test_webhooks.py -v

# Запуск интеграционных тестов
pytest tests/integration/ -v
```

### Ручное тестирование

```bash
# Запуск тестового скрипта
python scripts/test_webhook_server.py

# Тестирование с кастомным URL
python scripts/test_webhook_server.py http://localhost:8000
```

### Тестирование через curl

```bash
# Health check
curl -X GET http://localhost:8000/api/webhooks/amo/health

# Test endpoint
curl -X GET http://localhost:8000/api/webhooks/amo/test

# Тестовый webhook
curl -X POST http://localhost:8000/api/webhooks/amo \
  -H "Content-Type: application/json" \
  -H "X-Client-UUID: test-uuid" \
  -H "X-Signature: test-signature" \
  -H "X-Account-ID: test-account" \
  -d '{
    "leads": {
      "add": [{"id": 123, "name": "Test Lead"}]
    }
  }'
```

## 🔒 Безопасность

### Проверка подписи

Webhook проверяется с помощью HMAC-SHA256 подписи:

```python
def verify_webhook_signature(client_uuid, signature, account_id, client_secret):
    message = f"{client_uuid}|{account_id}"
    expected_signature = hmac.new(
        client_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
```

### Валидация данных

Все входящие данные проходят валидацию:

1. **Структура данных** - проверка формата JSON
2. **Обязательные поля** - проверка наличия ID
3. **Типы данных** - проверка типов полей
4. **Размер данных** - ограничение размера payload

## 📊 Обработка событий

### Поддерживаемые события

| Событие | Описание | Обработка |
|---------|----------|-----------|
| `leads.add` | Создание лида | Создание записи в БД |
| `leads.update` | Обновление лида | Обновление статуса и данных |
| `leads.delete` | Удаление лида | Помечание как удаленный |
| `contacts.add` | Создание контакта | Обновление информации о контакте |
| `contacts.update` | Обновление контакта | Обновление телефона/email |

### Маппинг статусов

| amoCRM Status ID | Внутренний статус | Описание |
|------------------|-------------------|----------|
| 1 | `new` | Новый лид |
| 2 | `contacted` | Первичный контакт |
| 3 | `presentation` | Презентация |
| 4 | `object_selected` | Выбор объекта |
| 5 | `reserved` | Резервирование |
| 6 | `deal` | Сделка |
| 7 | `completed` | Завершено |

### Обработка UTM меток

UTM метки автоматически извлекаются из кастомных полей:

```python
def _extract_utm_data(data):
    utm_mapping = {
        123458: "utm_source",    # UTM Source
        123459: "utm_medium",    # UTM Medium
        123460: "utm_campaign",  # UTM Campaign
        123461: "utm_content",   # UTM Content
        123462: "utm_term"       # UTM Term
    }
    # Извлечение и маппинг значений
```

## 📝 Логирование

### Уровни логирования

- **INFO** - Успешные операции
- **WARNING** - Предупреждения
- **ERROR** - Ошибки обработки
- **DEBUG** - Детальная отладка

### Примеры логов

```
INFO: Received webhook from amoCRM: {"leads": {"add": [{"id": 12345}]}}
INFO: Webhook signature verified for account: test-account
INFO: New lead created from amoCRM: 12345
INFO: Webhook processed 1 events in 0.15s
```

### Просмотр логов

```bash
# Docker
docker-compose logs -f backend

# Локально
tail -f logs/app.log

# Поиск ошибок
grep "ERROR" logs/app.log
```

## 🚨 Обработка ошибок

### Типы ошибок

| Код | Описание | Решение |
|-----|----------|---------|
| 400 | Невалидные данные | Проверить структуру JSON |
| 401 | Невалидная подпись | Проверить client_secret |
| 500 | Внутренняя ошибка | Проверить логи сервера |

### Retry логика

При ошибках обработки:

1. **Первая попытка** - немедленная обработка
2. **Вторая попытка** - через 5 секунд
3. **Третья попытка** - через 30 секунд
4. **Финальная ошибка** - запись в лог

### Мониторинг ошибок

```bash
# Подсчет ошибок
grep -c "ERROR" logs/app.log

# Статистика по типам ошибок
grep "ERROR" logs/app.log | awk '{print $NF}' | sort | uniq -c
```

## 🔄 Мониторинг и метрики

### Health check

```bash
# Проверка состояния сервиса
curl -X GET http://localhost:8000/api/webhooks/amo/health

# Автоматическая проверка
watch -n 30 'curl -s http://localhost:8000/api/webhooks/amo/health'
```

### Метрики производительности

- **Время обработки** - среднее время обработки webhook
- **Количество событий** - статистика по типам событий
- **Ошибки** - количество и типы ошибок
- **Доступность** - uptime сервиса

### Алерты

Настройте алерты для:

- Ошибок обработки webhook
- Высокого времени отклика
- Недоступности сервиса
- Ошибок БД

## 🔧 Troubleshooting

### Частые проблемы

#### 1. "Invalid signature"
**Причина:** Неправильный client_secret
**Решение:** Проверить настройки в amoCRM

#### 2. "Database connection failed"
**Причина:** Проблемы с БД
**Решение:** Проверить подключение и миграции

#### 3. "Field not found"
**Причина:** Кастомные поля не созданы
**Решение:** Создать поля с правильными ID

#### 4. "Webhook not received"
**Причина:** Неправильный URL или недоступность
**Решение:** Проверить URL и доступность сервера

### Диагностика

```bash
# Проверка статуса сервиса
curl -X GET http://localhost:8000/api/webhooks/amo/health

# Проверка логов
docker-compose logs backend | tail -50

# Проверка БД
docker-compose exec db psql -U asia -d asia_crm -c "SELECT COUNT(*) FROM leads;"

# Тест webhook
python scripts/test_webhook_server.py
```

## 📈 Оптимизация

### Производительность

1. **Асинхронная обработка** - использование async/await
2. **Батчинг** - группировка операций БД
3. **Кэширование** - кэш часто используемых данных
4. **Connection pooling** - пул соединений БД

### Масштабирование

1. **Горизонтальное масштабирование** - несколько инстансов
2. **Load balancing** - балансировка нагрузки
3. **Queue system** - очередь для обработки
4. **Database sharding** - шардинг БД

## 🔄 Обновления

### Обновление сервера

```bash
# Остановка сервиса
docker-compose down

# Обновление кода
git pull origin main

# Пересборка и запуск
docker-compose up -d --build

# Проверка статуса
docker-compose logs -f backend
```

### Миграции БД

```bash
# Запуск миграций
docker-compose exec backend alembic upgrade head

# Проверка статуса миграций
docker-compose exec backend alembic current
```

## 📞 Поддержка

### Контакты

- **Email:** support@asia-deals.com
- **Telegram:** @asia_deals_support
- **Документация:** `/docs`

### Полезные команды

```bash
# Полный статус системы
docker-compose ps

# Логи всех сервисов
docker-compose logs

# Перезапуск webhook сервера
docker-compose restart backend

# Проверка конфигурации
docker-compose config
```

---

**Готово к работе!** 🚀

Вебхук сервер настроен и готов к приему уведомлений от amoCRM.
