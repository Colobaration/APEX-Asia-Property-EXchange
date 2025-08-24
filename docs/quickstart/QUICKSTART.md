# 🚀 Быстрый старт интеграции с amoCRM

## ⚡ Быстрая настройка (5 минут)

### 1. Клонирование и установка
```bash
git clone <repository-url>
cd APEX-Asia-Property-EXchange-
make install
```

### 2. Настройка переменных окружения
```bash
cp env.example .env
# Отредактируйте .env файл с вашими данными amoCRM
```

### 3. Запуск приложения
```bash
make start
```

### 4. Авторизация в amoCRM
```bash
make amo-auth
```

### 5. Тестирование
```bash
make test-integration
```

## 📋 Что нужно настроить в amoCRM

### Обязательные настройки:
1. **Создать приложение** в amoCRM
2. **Настроить OAuth2 права**
3. **Создать кастомные поля** (см. таблицу ниже)
4. **Настроить webhook**

### Кастомные поля для создания:

| Сущность | Поле | ID | Тип |
|----------|------|----|-----|
| Контакты | Телефон | 123456 | Телефон |
| Контакты | Email | 123457 | Email |
| Сделки | UTM Source | 123458 | Текст |
| Сделки | UTM Medium | 123459 | Текст |
| Сделки | UTM Campaign | 123460 | Текст |

## 🔧 Основные команды

```bash
# Управление приложением
make start          # Запуск
make stop           # Остановка
make restart        # Перезапуск
make logs           # Просмотр логов

# Работа с amoCRM
make amo-auth       # Авторизация
make amo-status     # Статус авторизации
make amo-test       # Тест подключения

# Работа с лидами
make create-lead    # Создать тестовый лид
make get-leads      # Получить список лидов

# База данных
make migrate        # Применить миграции
make backup         # Резервная копия
make restore        # Восстановление

# Разработка
make test           # Запуск тестов
make format         # Форматирование кода
make lint           # Проверка кода
```

## 🧪 Тестирование интеграции

### Автоматическое тестирование
```bash
make test-integration
```

### Ручное тестирование
```bash
# Проверка статуса
curl http://localhost:8000/api/auth/amo/status

# Создание лида
curl -X POST http://localhost:8000/api/leads/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Тест", "phone": "+79001234567"}'

# Получение лидов
curl http://localhost:8000/api/leads/
```

## 🚨 Частые проблемы

### "amoCRM не авторизован"
```bash
make amo-auth  # Перейдите по ссылке и авторизуйтесь
```

### "Database connection failed"
```bash
make migrate   # Примените миграции
```

### "Invalid client_id"
Проверьте правильность Client ID в .env файле

### "Field not found"
Создайте кастомные поля в amoCRM с указанными ID

## 📞 Поддержка

- **Документация:** `docs/amocrm-integration-guide.md`
- **API документация:** `http://localhost:8000/docs`
- **Логи:** `make logs`
- **Статус:** `make health`

## 🎯 Следующие шаги

После успешной настройки:

1. **Настройте email воронки**
2. **Подключите WhatsApp API**
3. **Настройте аналитические дашборды**
4. **Проведите нагрузочное тестирование**

---

**Готово!** 🎉 Интеграция настроена и работает.
