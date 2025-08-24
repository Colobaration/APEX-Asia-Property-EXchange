# API Endpoints Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

### OAuth2 amoCRM
- `GET /api/auth/amo` - Начало OAuth2 авторизации
- `GET /api/auth/amo/callback` - Callback для получения токенов
- `POST /api/auth/amo/refresh` - Обновление access token
- `GET /api/auth/amo/status` - Проверка статуса авторизации

## Leads API

### Создание лида
```
POST /api/leads/
```

**Request Body:**
```json
{
  "name": "Иван Иванов",
  "phone": "+79001234567",
  "email": "ivan@example.com",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "asia_deals",
  "utm_content": "banner_1",
  "utm_term": "недвижимость азии"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Иван Иванов",
  "phone": "+79001234567",
  "email": "ivan@example.com",
  "amocrm_contact_id": 12345,
  "amocrm_lead_id": 67890,
  "status": "created"
}
```

### Получение лида
```
GET /api/leads/{lead_id}
```

## Webhooks API

### amoCRM Webhooks
```
POST /api/webhooks/amo
```

**Request Body:**
```json
{
  "leads": {
    "add": [...],
    "update": [...]
  },
  "contacts": {
    "add": [...],
    "update": [...]
  }
}
```

### Изменение статуса сделки
```
POST /api/webhooks/amo/lead-status-changed
```

**Query Parameters:**
- `lead_id` - ID сделки в amoCRM
- `status_id` - Новый статус

## Analytics API

### CPL (Cost Per Lead)
```
GET /api/analytics/cpl
```

**Query Parameters:**
- `start_date` - Начальная дата (YYYY-MM-DD)
- `end_date` - Конечная дата (YYYY-MM-DD)
- `utm_source` - Фильтр по источнику

**Response:**
```json
{
  "metric": "CPL",
  "period": {
    "start": "2024-01-01T00:00:00",
    "end": "2024-01-31T23:59:59"
  },
  "value": 150.50,
  "leads_count": 100,
  "total_cost": 15050.00,
  "breakdown": {
    "google": 120.00,
    "facebook": 180.00
  }
}
```

### Conversion Rate
```
GET /api/analytics/cr
```

**Query Parameters:**
- `start_date` - Начальная дата
- `end_date` - Конечная дата
- `pipeline_id` - ID воронки

### ROI (Return on Investment)
```
GET /api/analytics/roi
```

**Query Parameters:**
- `start_date` - Начальная дата
- `end_date` - Конечная дата
- `utm_source` - Фильтр по источнику

### Dashboard Data
```
GET /api/analytics/dashboard
```

**Query Parameters:**
- `period` - Период (7d, 30d, 90d)

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error description"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per API key

## Authentication

Для защищенных endpoints требуется Bearer token:

```
Authorization: Bearer <your_access_token>
```
