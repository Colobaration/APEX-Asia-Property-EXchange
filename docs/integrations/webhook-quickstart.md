# ⚡ Быстрый старт вебхук сервера AmoCRM

## 🚀 За 5 минут

### 1. Запуск сервера
```bash
# Запуск всех сервисов
make start

# Проверка статуса
make status
```

### 2. Проверка здоровья
```bash
# Проверка webhook сервера
make webhook-health

# Тестирование endpoints
make webhook-status
```

### 3. Тестирование
```bash
# Запуск всех тестов
make webhook-test

# Симуляция webhook
make webhook-simulate
```

### 4. Мониторинг
```bash
# Просмотр логов
make webhook-logs

# Общий мониторинг
make monitor
```

## 🔧 Настройка

### Переменные окружения (.env)
```bash
# amoCRM
AMOCRM_CLIENT_ID=your_client_id
AMOCRM_CLIENT_SECRET=your_client_secret
AMOCRM_DOMAIN=your-company.amocrm.ru

# База данных
DB_URL=postgresql://asia:asia@db:5432/asia_crm
```

### Webhook в amoCRM
```
URL: http://your-domain.com/api/webhooks/amo
События: leads.add, leads.update, contacts.add, contacts.update
```

## 📡 API Endpoints

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/webhooks/amo` | POST | Основной webhook |
| `/api/webhooks/amo/health` | GET | Health check |
| `/api/webhooks/amo/test` | GET | Тестовый endpoint |

## 🧪 Тестирование

### Автоматические тесты
```bash
# Unit тесты
cd backend && pytest tests/unit/test_webhooks.py

# Интеграционные тесты
pytest tests/integration/
```

### Ручное тестирование
```bash
# Тестовый скрипт
python scripts/test_webhook_server.py

# curl команды
curl -X GET http://localhost:8000/api/webhooks/amo/health
```

## 📊 Поддерживаемые события

- ✅ `leads.add` - Создание лида
- ✅ `leads.update` - Обновление лида  
- ✅ `leads.delete` - Удаление лида
- ✅ `contacts.add` - Создание контакта
- ✅ `contacts.update` - Обновление контакта

## 🔒 Безопасность

- HMAC-SHA256 подпись
- Валидация данных
- Логирование всех операций
- Обработка ошибок

## 📝 Логи

```bash
# Просмотр логов
make webhook-logs

# Поиск ошибок
docker-compose logs backend | grep ERROR

# Статистика
docker-compose logs backend | grep "webhook processed"
```

## 🚨 Troubleshooting

### Проблема: "Invalid signature"
```bash
# Проверьте client_secret в .env
# Убедитесь, что webhook настроен правильно в amoCRM
```

### Проблема: "Database connection failed"
```bash
# Проверьте статус БД
make status

# Запустите миграции
make migrate
```

### Проблема: "Webhook not received"
```bash
# Проверьте доступность сервера
make webhook-health

# Проверьте URL в amoCRM
# Убедитесь, что порт 8000 открыт
```

## 📞 Поддержка

- **Документация:** `docs/webhook-server-setup.md`
- **Тесты:** `scripts/test_webhook_server.py`
- **Логи:** `make webhook-logs`

---

**Готово!** 🎉 Вебхук сервер работает и готов к приему данных от amoCRM.
