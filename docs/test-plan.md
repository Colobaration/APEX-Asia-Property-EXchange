# Test Plan - Asia Deals CRM Integration

## Обзор тестирования

### Цели тестирования
- Проверка корректности интеграции с amoCRM
- Валидация обработки лидов и webhooks
- Тестирование аналитических метрик
- Проверка email и WhatsApp интеграций
- Нагрузочное тестирование API

## Типы тестов

### 1. Unit Tests

#### Backend (Python/FastAPI)
```bash
# Запуск unit тестов
cd backend
pytest tests/unit/ -v

# Покрытие кода
pytest --cov=app tests/unit/ --cov-report=html
```

**Тестируемые модули:**
- `app.api.leads` - API для лидов
- `app.api.auth` - OAuth2 аутентификация
- `app.api.webhooks` - Обработка webhooks
- `app.api.analytics` - Аналитические API
- `app.integrations.amo.client` - amoCRM клиент
- `app.models` - Модели данных

#### Frontend (React/Next.js)
```bash
# Запуск unit тестов
cd frontend
npm test

# Покрытие кода
npm run test:coverage
```

**Тестируемые компоненты:**
- Lead Form компонент
- Dashboard компоненты
- API клиенты
- Утилиты и хелперы

### 2. Integration Tests

#### API Integration Tests
```bash
# Запуск integration тестов
cd backend
pytest tests/integration/ -v
```

**Тестовые сценарии:**
1. **Создание лида**
   - POST /api/leads/ с валидными данными
   - Проверка создания в amoCRM
   - Проверка записи в БД

2. **OAuth2 авторизация**
   - GET /api/auth/amo
   - GET /api/auth/amo/callback
   - Проверка получения токенов

3. **Webhooks обработка**
   - POST /api/webhooks/amo
   - Проверка обновления статусов
   - Проверка синхронизации данных

#### Database Integration Tests
```bash
# Тестирование с тестовой БД
pytest tests/integration/test_db.py -v
```

**Тестовые сценарии:**
- Создание/чтение/обновление лидов
- Создание/чтение/обновление сделок
- Миграции базы данных
- Связи между таблицами

### 3. E2E Tests

#### Frontend E2E Tests
```bash
# Запуск E2E тестов
cd frontend
npm run test:e2e
```

**Тестовые сценарии:**
1. **Лендинг**
   - Загрузка главной страницы
   - Заполнение формы лида
   - Отправка формы
   - Проверка редиректа

2. **CRM Dashboard**
   - Авторизация пользователя
   - Просмотр списка лидов
   - Фильтрация и поиск
   - Изменение статусов

3. **Аналитика**
   - Загрузка дашборда
   - Фильтрация по периодам
   - Экспорт отчетов

#### API E2E Tests
```bash
# Тестирование полного API flow
pytest tests/e2e/test_api_flow.py -v
```

**Тестовые сценарии:**
1. **Полный цикл лида**
   - Создание лида
   - Обработка в amoCRM
   - Изменение статуса
   - Расчет метрик

2. **Аналитические метрики**
   - Расчет CPL
   - Расчет CR
   - Расчет ROI
   - Проверка корректности

### 4. Performance Tests

#### Load Testing
```bash
# Нагрузочное тестирование API
cd backend
locust -f tests/performance/locustfile.py
```

**Тестовые сценарии:**
- 100 одновременных пользователей
- 1000 запросов в минуту
- Тестирование создания лидов
- Тестирование аналитических API

#### Stress Testing
```bash
# Стресс-тестирование
pytest tests/performance/test_stress.py -v
```

**Тестовые сценарии:**
- Максимальная нагрузка на API
- Тестирование под высоким давлением
- Проверка стабильности системы

## Позитивные сценарии

### 1. Создание лида
```python
# Позитивный сценарий
def test_create_lead_success():
    lead_data = {
        "name": "Иван Иванов",
        "phone": "+79001234567",
        "email": "ivan@example.com",
        "utm_source": "google",
        "utm_medium": "cpc"
    }
    
    response = client.post("/api/leads/", json=lead_data)
    assert response.status_code == 200
    
    lead = response.json()
    assert lead["name"] == "Иван Иванов"
    assert lead["amocrm_contact_id"] is not None
    assert lead["amocrm_lead_id"] is not None
```

### 2. OAuth2 авторизация
```python
# Позитивный сценарий
def test_oauth2_flow():
    # 1. Получение auth URL
    response = client.get("/api/auth/amo")
    assert response.status_code == 200
    
    # 2. Callback с кодом
    response = client.get("/api/auth/amo/callback?code=test_code")
    assert response.status_code == 200
```

### 3. Webhook обработка
```python
# Позитивный сценарий
def test_webhook_processing():
    webhook_data = {
        "leads": {
            "add": [{"id": 123, "status_id": 2}]
        }
    }
    
    response = client.post("/api/webhooks/amo", json=webhook_data)
    assert response.status_code == 200
```

## Негативные сценарии

### 1. Невалидные данные лида
```python
# Негативный сценарий
def test_create_lead_invalid_data():
    # Отсутствует обязательное поле
    lead_data = {
        "name": "Иван Иванов"
        # Отсутствует phone
    }
    
    response = client.post("/api/leads/", json=lead_data)
    assert response.status_code == 422
    
    # Невалидный телефон
    lead_data = {
        "name": "Иван Иванов",
        "phone": "invalid_phone"
    }
    
    response = client.post("/api/leads/", json=lead_data)
    assert response.status_code == 422
```

### 2. Ошибки amoCRM
```python
# Негативный сценарий
def test_amocrm_error():
    # Неверные токены
    with patch('app.integrations.amo.client.AmoCRMClient._get_access_token') as mock:
        mock.side_effect = Exception("Invalid token")
        
        lead_data = {
            "name": "Иван Иванов",
            "phone": "+79001234567"
        }
        
        response = client.post("/api/leads/", json=lead_data)
        assert response.status_code == 500
```

### 3. Ошибки базы данных
```python
# Негативный сценарий
def test_database_error():
    # Недоступность БД
    with patch('app.core.db.get_db') as mock:
        mock.side_effect = Exception("Database connection failed")
        
        response = client.get("/api/leads/1")
        assert response.status_code == 500
```

## Тестовые данные

### Фикстуры
```python
# conftest.py
@pytest.fixture
def sample_lead_data():
    return {
        "name": "Тест Тестов",
        "phone": "+79001234567",
        "email": "test@example.com",
        "utm_source": "test_source",
        "utm_medium": "test_medium",
        "utm_campaign": "test_campaign"
    }

@pytest.fixture
def sample_webhook_data():
    return {
        "leads": {
            "add": [
                {
                    "id": 123,
                    "status_id": 2,
                    "name": "Тестовая сделка"
                }
            ]
        }
    }
```

## Автоматизация тестирования

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=app
      
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Тестовое окружение
```bash
# Запуск тестового окружения
docker-compose -f docker-compose.test.yml up -d

# Остановка тестового окружения
docker-compose -f docker-compose.test.yml down
```

## Метрики качества

### Покрытие кода
- **Цель**: > 80% покрытия
- **Backend**: pytest --cov=app
- **Frontend**: npm run test:coverage

### Время выполнения тестов
- **Unit тесты**: < 30 секунд
- **Integration тесты**: < 2 минут
- **E2E тесты**: < 5 минут

### Стабильность тестов
- **Цель**: > 95% прохождения
- **Flaky тесты**: < 1%

## Отчеты

### Автоматические отчеты
- HTML отчеты покрытия кода
- JUnit XML отчеты для CI/CD
- Allure отчеты для E2E тестов

### Ручные отчеты
- Тест-кейсы в TestRail
- Баг-репорты в Jira
- Документация тестов

## Проверка задач Cursor'ом

- Запуск шаблона самопроверки: `.cursor/templates/review-prompt.md`.
- Локальные команды проверки: `make check`.
- Критерии приёма (DoD):
  - Тесты покрывают happy path + 1–2 edge cases.
  - `make check` зелёный.
  - Документация/README обновлены.
