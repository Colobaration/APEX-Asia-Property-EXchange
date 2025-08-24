# 🧪 Тестирование APEX

## 🎯 Обзор

Эта директория содержит документацию по тестированию системы APEX Asia Property Exchange.

## 📁 Структура

```
docs/testing/
├── README.md                    # Этот файл - обзор тестирования
└── test-plan.md                 # План тестирования
```

## 📋 Документация по тестированию

### **test-plan.md** - План тестирования
**Назначение:** Полный план тестирования системы APEX

**Содержит:**
- ✅ Unit тесты
- ✅ Integration тесты
- ✅ E2E тесты
- ✅ Performance тесты
- ✅ Security тесты

**Для кого:** QA инженеры, разработчики

## 🧪 Типы тестирования

### **1. Unit тесты**
```bash
# Backend тесты
cd backend
pytest tests/unit/

# Frontend тесты
cd frontend
npm test
```

### **2. Integration тесты**
```bash
# API тесты
cd backend
pytest tests/integration/

# Database тесты
pytest tests/integration/test_database.py
```

### **3. E2E тесты**
```bash
# Playwright тесты
cd frontend
npm run test:e2e

# Cypress тесты (если настроен)
npm run cypress:run
```

### **4. Performance тесты**
```bash
# Load тесты
cd backend
pytest tests/performance/

# Stress тесты
pytest tests/performance/test_stress.py
```

## 🚀 Быстрый старт

### **Запуск всех тестов**
```bash
# Backend
make test-backend

# Frontend
make test-frontend

# Все тесты
make test
```

### **Запуск с покрытием**
```bash
# Backend с coverage
cd backend
pytest --cov=app --cov-report=html

# Frontend с coverage
cd frontend
npm run test:coverage
```

### **Запуск конкретных тестов**
```bash
# Конкретный тест
pytest tests/unit/test_auth.py::test_login

# Тесты по маркеру
pytest -m "integration"

# Тесты по паттерну
pytest -k "test_auth"
```

## 📊 Покрытие кода

### **Backend покрытие**
- **Цель:** 80% покрытия
- **Отчет:** `backend/htmlcov/index.html`
- **Файл:** `backend/coverage.xml`

### **Frontend покрытие**
- **Цель:** 70% покрытия
- **Отчет:** `frontend/coverage/lcov-report/index.html`
- **Файл:** `frontend/coverage/coverage-final.json`

## 🔧 Конфигурация тестов

### **Backend (pytest)**
```ini
# backend/pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers --verbose --cov=app --cov-report=term-missing
markers =
    unit: Unit тесты
    integration: Integration тесты
    e2e: End-to-end тесты
    slow: Медленные тесты
```

### **Frontend (Jest)**
```json
// frontend/jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
}
```

## 🧪 Тестовые данные

### **Фикстуры**
```python
# backend/tests/conftest.py
@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }

@pytest.fixture
def test_lead():
    return {
        "name": "Test Lead",
        "email": "lead@example.com",
        "phone": "+1234567890"
    }
```

### **Моки**
```python
# Мокирование внешних сервисов
@patch('app.integrations.amo.client.AmoCRMClient')
def test_amocrm_integration(mock_client):
    mock_client.return_value.create_contact.return_value = {"id": 123}
    # тест
```

## 🔒 Security тесты

### **Аутентификация**
```bash
# Тест JWT токенов
pytest tests/security/test_jwt.py

# Тест OAuth2
pytest tests/security/test_oauth.py
```

### **Webhook безопасность**
```bash
# Тест подписи webhook'ов
pytest tests/security/test_webhook_signature.py

# Тест rate limiting
pytest tests/security/test_rate_limit.py
```

## 📈 Performance тесты

### **Load тесты**
```bash
# Тест API endpoints
pytest tests/performance/test_api_load.py

# Тест базы данных
pytest tests/performance/test_database_load.py
```

### **Stress тесты**
```bash
# Тест под нагрузкой
pytest tests/performance/test_stress.py

# Тест памяти
pytest tests/performance/test_memory.py
```

## 🚨 Troubleshooting

### **Проблемы с тестами**
```bash
# Проверить зависимости
pip install -r requirements.txt
npm install

# Очистить кэш
pytest --cache-clear
npm run test:clear

# Запустить с verbose
pytest -v
npm run test:verbose
```

### **Проблемы с покрытием**
```bash
# Проверить конфигурацию coverage
pytest --cov=app --cov-report=term-missing

# Генерировать HTML отчет
pytest --cov=app --cov-report=html
```

### **Проблемы с E2E тестами**
```bash
# Проверить браузер
npx playwright install

# Запустить в режиме отладки
npx playwright test --debug

# Запустить с видео
npx playwright test --video=on
```

## 📊 Отчеты

### **Автоматические отчеты**
- **Coverage:** генерируется автоматически
- **Test results:** в GitHub Actions
- **Performance:** в отдельном отчете

### **Ручные отчеты**
```bash
# Генерировать отчет
make test-report

# Открыть отчет
open backend/htmlcov/index.html
open frontend/coverage/lcov-report/index.html
```

## 🔗 Связанная документация

- [CI/CD документация](../cicd/README.md) - автоматизация тестирования
- [Настройка](../setup/README.md) - настройка компонентов
- [Архитектура](../architecture/README.md) - архитектура системы
- [Быстрый старт](../quickstart/README.md) - быстрый старт

## 📞 Поддержка

При возникновении проблем:

1. Проверьте зависимости и конфигурацию
2. Запустите тесты с verbose режимом
3. Проверьте логи тестов
4. Обратитесь к документации в соответствующих файлах
5. Создайте issue в репозитории

---

**Тестирование системы APEX настроено! 🎉**
