# 🔗 Интеграции APEX

## 🎯 Обзор

Эта директория содержит документацию по интеграциям системы APEX Asia Property Exchange с внешними сервисами.

## 📁 Структура

```
docs/integrations/
├── README.md                    # Этот файл - обзор интеграций
├── amocrm-integration-guide.md  # Полное руководство по AmoCRM
├── amocrm-setup.md              # Настройка AmoCRM
├── webhook-quickstart.md        # Быстрый старт webhook'ов
└── webhook-server-setup.md      # Настройка webhook сервера
```

## 📋 Документация по интеграциям

### **amocrm-integration-guide.md** - Полное руководство по AmoCRM
**Назначение:** Подробное руководство по интеграции с AmoCRM

**Содержит:**
- ✅ OAuth2 аутентификация
- ✅ API endpoints и методы
- ✅ Синхронизация данных
- ✅ Обработка webhook'ов
- ✅ Обработка ошибок и retry логика

**Для кого:** Разработчики интеграций, backend разработчики

### **amocrm-setup.md** - Настройка AmoCRM
**Назначение:** Пошаговая инструкция по настройке AmoCRM

**Содержит:**
- ✅ Создание приложения в AmoCRM
- ✅ Настройка OAuth2
- ✅ Конфигурация webhook'ов
- ✅ Тестирование интеграции

**Для кого:** DevOps инженеры, администраторы

### **webhook-quickstart.md** - Быстрый старт webhook'ов
**Назначение:** Быстрое начало работы с webhook'ами

**Содержит:**
- ✅ Основные концепции webhook'ов
- ✅ Быстрая настройка
- ✅ Примеры использования
- ✅ Troubleshooting

**Для кого:** Разработчики, начинающие с webhook'ов

### **webhook-server-setup.md** - Настройка webhook сервера
**Назначение:** Подробная настройка webhook сервера

**Содержит:**
- ✅ Архитектура webhook сервера
- ✅ Настройка безопасности
- ✅ Обработка событий
- ✅ Мониторинг и логирование

**Для кого:** DevOps инженеры, backend разработчики

## 🔗 Поддерживаемые интеграции

### **1. AmoCRM**
- ✅ OAuth2 аутентификация
- ✅ REST API интеграция
- ✅ Webhook обработка
- ✅ Синхронизация лидов и сделок
- ✅ Кастомные поля

### **2. WhatsApp Business API**
- ✅ Отправка сообщений
- ✅ Получение сообщений
- ✅ Статусы доставки
- ✅ Медиа файлы

### **3. Telegram Bot API**
- ✅ Отправка уведомлений
- ✅ Команды бота
- ✅ Inline клавиатуры
- ✅ Webhook режим

### **4. Email (SMTP)**
- ✅ Отправка email
- ✅ HTML шаблоны
- ✅ Вложения
- ✅ Массовая рассылка

## 🚀 Быстрый старт

### **Настройка AmoCRM**
```bash
# 1. Создать приложение в AmoCRM
# 2. Настроить OAuth2
# 3. Получить токены

# Настройка переменных окружения
AMOCRM_CLIENT_ID=your_client_id
AMOCRM_CLIENT_SECRET=your_client_secret
AMOCRM_DOMAIN=your_domain.amocrm.ru
AMOCRM_REDIRECT_URI=http://localhost:8000/api/auth/amo/callback
```

### **Настройка webhook'ов**
```bash
# Настройка webhook для AmoCRM
curl -X POST http://localhost:8000/api/webhooks/amocrm/setup

# Тестирование webhook
curl -X POST http://localhost:8000/api/webhooks/amocrm/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### **Настройка WhatsApp**
```bash
# Настройка WhatsApp API
WHATSAPP_API_URL=https://api.whatsapp.com
WHATSAPP_API_KEY=your_api_key
WHATSAPP_PHONE_NUMBER=your_phone_number
```

## 🔧 Конфигурация

### **Переменные окружения**
```bash
# AmoCRM
AMOCRM_CLIENT_ID=your_client_id
AMOCRM_CLIENT_SECRET=your_client_secret
AMOCRM_DOMAIN=your_domain.amocrm.ru
AMOCRM_REDIRECT_URI=http://localhost:8000/api/auth/amo/callback

# WhatsApp
WHATSAPP_API_URL=https://api.whatsapp.com
WHATSAPP_API_KEY=your_api_key
WHATSAPP_PHONE_NUMBER=your_phone_number

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_DEFAULT_CHAT_ID=your_chat_id

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 🧪 Тестирование

### **Тестирование AmoCRM**
```bash
# Проверка аутентификации
curl http://localhost:8000/api/auth/amo/status

# Тест API
curl http://localhost:8000/api/leads/ \
  -H "Authorization: Bearer your_token"

# Тест webhook
curl -X POST http://localhost:8000/api/webhooks/amocrm/test
```

### **Тестирование webhook'ов**
```bash
# Тест webhook сервера
curl -X POST http://localhost:8000/api/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "data": {"test": "value"}}'
```

### **Тестирование уведомлений**
```bash
# Тест WhatsApp
curl -X POST http://localhost:8000/api/notifications/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "message": "Test message"}'

# Тест Telegram
curl -X POST http://localhost:8000/api/notifications/telegram/test \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "123456789", "message": "Test message"}'
```

## 🚨 Troubleshooting

### **Проблемы с AmoCRM**
```bash
# Проверить токены
curl http://localhost:8000/api/auth/amo/status

# Обновить токены
curl -X POST http://localhost:8000/api/auth/amo/refresh

# Проверить логи
docker-compose logs backend | grep amocrm
```

### **Проблемы с webhook'ами**
```bash
# Проверить статус webhook сервера
curl http://localhost:8000/api/webhooks/status

# Проверить логи webhook'ов
docker-compose logs backend | grep webhook

# Проверить настройки безопасности
curl http://localhost:8000/api/webhooks/security/check
```

### **Проблемы с уведомлениями**
```bash
# Проверить статус WhatsApp
curl http://localhost:8000/api/notifications/whatsapp/status

# Проверить статус Telegram
curl http://localhost:8000/api/notifications/telegram/status

# Проверить логи уведомлений
docker-compose logs backend | grep notification
```

## 📊 Мониторинг

### **Метрики интеграций**
```bash
# Статус всех интеграций
curl http://localhost:8000/api/integrations/status

# Метрики AmoCRM
curl http://localhost:8000/api/integrations/amocrm/metrics

# Метрики webhook'ов
curl http://localhost:8000/api/webhooks/metrics
```

### **Логи**
```bash
# Логи интеграций
docker-compose logs backend | grep -E "(amocrm|webhook|notification)"

# Логи AmoCRM
docker-compose logs backend | grep amocrm

# Логи webhook'ов
docker-compose logs backend | grep webhook
```

## 🔒 Безопасность

### **Webhook безопасность**
- ✅ Проверка подписи webhook'ов
- ✅ Валидация IP адресов
- ✅ Rate limiting
- ✅ Idempotency keys

### **OAuth2 безопасность**
- ✅ Secure token storage
- ✅ Token refresh
- ✅ Scope validation
- ✅ Error handling

## 🔗 Связанная документация

- [Настройка](../setup/README.md) - настройка компонентов
- [CI/CD документация](../cicd/README.md) - автоматизация
- [Архитектура](../architecture/README.md) - архитектура системы
- [Быстрый старт](../quickstart/README.md) - быстрый старт

## 📞 Поддержка

При возникновении проблем:

1. Проверьте переменные окружения
2. Проверьте логи интеграций
3. Убедитесь в корректности настроек внешних сервисов
4. Обратитесь к документации в соответствующих файлах
5. Создайте issue в репозитории

---

**Интеграции системы APEX настроены! 🎉**
