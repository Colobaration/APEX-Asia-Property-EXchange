# 🔧 Настройка APEX

## 🎯 Обзор

Эта директория содержит документацию по настройке различных компонентов системы APEX Asia Property Exchange.

## 📁 Структура

```
docs/setup/
├── README.md                    # Этот файл - обзор настройки
├── MIGRATION_SYSTEM_SUMMARY.md  # Система автоматических миграций
├── API_SERVER_README.md         # Настройка API сервера
└── WEBHOOK_SETUP.md             # Настройка webhook'ов
```

## 📋 Документация по настройке

### **MIGRATION_SYSTEM_SUMMARY.md** - Система миграций
**Назначение:** Полная документация по системе автоматических миграций базы данных

**Содержит:**
- ✅ Автоматические миграции при запуске контейнера
- ✅ Entrypoint скрипт для Docker
- ✅ Управление миграциями через Makefile
- ✅ Тестирование системы миграций
- ✅ Best practices и рекомендации

**Для кого:** DevOps инженеры, разработчики backend

### **API_SERVER_README.md** - API сервер
**Назначение:** Документация по настройке и запуску API сервера

**Содержит:**
- ✅ Быстрый запуск через скрипты
- ✅ Конфигурация переменных окружения
- ✅ API endpoints и их описание
- ✅ Структура проекта backend
- ✅ Отладка и мониторинг

**Для кого:** Разработчики, DevOps инженеры

### **WEBHOOK_SETUP.md** - Настройка webhook'ов
**Назначение:** Инструкции по настройке webhook интеграций

**Содержит:**
- ✅ Настройка webhook'ов для amoCRM
- ✅ Конфигурация безопасности
- ✅ Тестирование webhook'ов
- ✅ Troubleshooting

**Для кого:** Разработчики интеграций, DevOps инженеры

## 🚀 Быстрый старт

### **1. Настройка миграций**
```bash
# Применить миграции
make migrate

# Создать новую миграцию
make migrate-create MESSAGE="Add new table"

# Проверить статус
make migrate-status
```

### **2. Запуск API сервера**
```bash
# Быстрый запуск
./scripts/start-api.sh

# Просмотр логов
./scripts/start-api.sh logs

# Проверка статуса
./scripts/start-api.sh status
```

### **3. Настройка webhook'ов**
```bash
# Настройка amoCRM webhook
curl -X POST http://localhost:8000/api/webhooks/amocrm/setup

# Тестирование webhook
curl -X POST http://localhost:8000/api/webhooks/amocrm/test
```

## 🔧 Конфигурация

### **Переменные окружения**
Все настройки находятся в файлах:
- `.env` - локальная разработка
- `.env.staging` - staging окружение
- `.env.production` - production окружение

### **Основные настройки**
```bash
# База данных
DB_URL=postgresql://asia:asia@db:5432/asia_crm_staging

# amoCRM
AMOCRM_CLIENT_ID=your_client_id
AMOCRM_CLIENT_SECRET=your_client_secret
AMOCRM_DOMAIN=your_domain.amocrm.ru

# Безопасность
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret
```

## 🧪 Тестирование

### **Тестирование миграций**
```bash
# Создать тестовую миграцию
make migrate-create MESSAGE="Test migration"

# Применить миграции
make migrate

# Проверить результат
make migrate-status
```

### **Тестирование API**
```bash
# Health check
curl http://localhost:8000/health

# API документация
open http://localhost:8000/docs

# Тест endpoints
curl http://localhost:8000/api/leads/
```

### **Тестирование webhook'ов**
```bash
# Тест amoCRM webhook
curl -X POST http://localhost:8000/api/webhooks/amocrm/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## 🚨 Troubleshooting

### **Проблемы с миграциями**
```bash
# Проверить статус БД
docker-compose exec db pg_isready -U asia

# Проверить логи
docker-compose logs backend

# Откатить миграцию
make migrate-down
```

### **Проблемы с API**
```bash
# Проверить статус контейнеров
docker-compose ps

# Перезапустить сервисы
docker-compose restart backend

# Проверить переменные окружения
docker-compose exec backend env
```

### **Проблемы с webhook'ами**
```bash
# Проверить логи webhook'ов
docker-compose logs backend | grep webhook

# Проверить настройки amoCRM
curl http://localhost:8000/api/auth/amo/status
```

## 📊 Мониторинг

### **Логи**
```bash
# Все сервисы
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Фильтр по миграциям
docker-compose logs backend | grep -i migration
```

### **Статус сервисов**
```bash
# Health check
curl http://localhost:8000/health

# Статус БД
docker-compose exec db pg_isready -U asia

# Статус Redis
docker-compose exec redis redis-cli ping
```

## 🔗 Связанная документация

- [CI/CD документация](../cicd/README.md) - настройка CI/CD
- [Архитектура](../ARCHITECTURE.md) - архитектура системы
- [Безопасность](../SECURITY.md) - безопасность
- [Быстрый старт](../quickstart/README.md) - быстрый старт

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи сервисов
2. Убедитесь, что все переменные окружения корректны
3. Проверьте документацию в соответствующих файлах
4. Создайте issue в репозитории

---

**Настройка системы APEX завершена! 🎉**
