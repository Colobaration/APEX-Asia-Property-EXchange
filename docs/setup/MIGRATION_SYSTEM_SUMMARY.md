# 🚀 Система автоматических миграций - APEX Asia Property Exchange

## 📋 Обзор

Создана полноценная система автоматических миграций базы данных для проекта APEX Asia Property Exchange. Система использует **Alembic** и автоматически применяет миграции при запуске контейнера.

## ✅ Что реализовано

### 🔧 Автоматические миграции при запуске
- **Entrypoint скрипт**: `backend/docker-entrypoint.sh`
- **Ожидание готовности БД**: Автоматическое ожидание PostgreSQL
- **Проверка и применение миграций**: Автоматическое применение новых миграций
- **Инициализация БД**: Создание базы данных при необходимости

### 📁 Структура файлов

```
backend/
├── docker-entrypoint.sh          # Entrypoint для Docker контейнера
├── scripts/
│   ├── run_migrations.py         # Скрипт выполнения миграций
│   ├── init_db.py               # Скрипт инициализации БД
│   └── create_migration.py      # Скрипт создания новых миграций
├── alembic/
│   ├── versions/                # Файлы миграций
│   │   ├── 196dfdb50f6c_initial_migration.py
│   │   ├── 20240101000000_add_amocrm_tokens.py
│   │   └── 20250101000000_add_test_table.py
│   ├── env.py                   # Конфигурация Alembic
│   └── script.py.mako          # Шаблон миграций
├── alembic.ini                 # Конфигурация Alembic
├── Makefile                    # Удобные команды для управления
└── docs/
    └── MIGRATIONS.md           # Подробная документация
```

### 🐳 Docker интеграция

#### Dockerfile обновлен:
```dockerfile
# Делаем entrypoint скрипт исполняемым
RUN chmod +x docker-entrypoint.sh

# Используем entrypoint скрипт
ENTRYPOINT ["./docker-entrypoint.sh"]
```

#### docker-compose.staging.yml обновлен:
```yaml
environment:
  - ENVIRONMENT=staging
  - PYTHONPATH=/app
  - LOG_LEVEL=${LOG_LEVEL:-INFO}
  - INIT_DB=true  # Включить автоматическую инициализацию
```

## 🔄 Процесс запуска

### 1. Запуск контейнера
```bash
docker-compose -f docker-compose.staging.yml up -d backend
```

### 2. Автоматические шаги
1. **📋 Проверка переменных окружения**
2. **⏳ Ожидание готовности базы данных**
3. **🔄 Выполнение миграций**
4. **🗄️ Инициализация БД (если INIT_DB=true)**
5. **🚀 Запуск FastAPI приложения**

### 3. Логи процесса
```
🚀 APEX Asia Property Exchange - Backend Entrypoint
==================================================
[2025-08-24 16:03:05] 📋 Проверка переменных окружения...
[2025-08-24 16:03:05] 🌍 Окружение: staging
[2025-08-24 16:03:05] 🗄️ База данных: postgresql://asia:asia@db:5432/asia_crm_staging
[2025-08-24 16:03:05] ⏳ Ожидание готовности базы данных...
[2025-08-24 16:03:05] ✅ База данных готова!
[2025-08-24 16:03:05] 🔄 Запуск миграций базы данных...
[2025-08-24 16:03:06] ✅ Миграции выполнены успешно!
[2025-08-24 16:03:06] 🗄️ Инициализация базы данных...
[2025-08-24 16:03:06] ✅ База данных инициализирована успешно!
[2025-08-24 16:03:06] 🎉 Инициализация завершена успешно!
[2025-08-24 16:03:06] 🚀 Запуск FastAPI приложения...
```

## 🛠️ Управление миграциями

### Использование Makefile

```bash
# Показать справку
make help

# Выполнить все миграции
make migrate

# Создать новую миграцию
make migrate-create MESSAGE="Add new table"

# Показать статус миграций
make migrate-status

# Откатить последнюю миграцию
make migrate-down

# Инициализировать БД
make init-db
```

### Использование скриптов напрямую

```bash
# Выполнить миграции
python scripts/run_migrations.py

# Инициализировать БД
python scripts/init_db.py

# Создать миграцию
python scripts/create_migration.py "Add new table"
```

### Docker команды

```bash
# Выполнить миграции в контейнере
make docker-migrate

# Инициализировать БД в контейнере
make docker-init-db

# Или напрямую
docker-compose -f docker-compose.staging.yml exec backend python scripts/run_migrations.py
```

## 🧪 Тестирование системы

### ✅ Успешно протестировано:

1. **Автоматическое применение миграций при запуске**
   - Создана тестовая миграция `20250101000000_add_test_table.py`
   - Миграция автоматически применилась при перезапуске контейнера
   - Создана таблица `test_migration_demo`

2. **Откат миграций**
   - Успешно откачена миграция: `downgrade 20250101000000 -> 20240101000000`
   - Таблица `test_migration_demo` удалена

3. **Повторное применение миграций**
   - Миграция успешно применена обратно
   - Таблица `test_migration_demo` создана снова

### 📊 Текущее состояние БД:
```sql
              List of relations
 Schema |        Name         | Type  | Owner 
--------+---------------------+-------+-------
 public | alembic_version     | table | asia
 public | amocrm_tokens       | table | asia
 public | deals               | table | asia
 public | leads               | table | asia
 public | test_migration_demo | table | asia
```

## 🔧 Конфигурация

### Переменные окружения

```bash
# Обязательные
DATABASE_URL=postgresql://asia:asia@db:5432/asia_crm_staging
ENVIRONMENT=staging

# Опциональные
INIT_DB=true                    # Включить инициализацию БД
LOG_LEVEL=INFO                  # Уровень логирования
```

### Alembic конфигурация

```ini
# backend/alembic.ini
sqlalchemy.url = postgresql://asia:asia@db:5432/asia_crm_staging
script_location = alembic
```

## 🚀 Best Practices

### ✅ Рекомендации

1. **Всегда создавайте миграции для изменений схемы**
2. **Используйте описательные сообщения для миграций**
3. **Тестируйте миграции на staging перед продакшеном**
4. **Делайте backup перед применением миграций в продакшене**
5. **Используйте транзакции для сложных миграций**

### ❌ Избегайте

1. **Изменения схемы БД напрямую без миграций**
2. **Удаления файлов миграций из истории**
3. **Применения миграций без тестирования**
4. **Игнорирования ошибок при выполнении миграций**

## 📈 Мониторинг

### Логи миграций

```bash
# Просмотр логов backend
docker-compose -f docker-compose.staging.yml logs backend

# Фильтр по миграциям
docker-compose -f docker-compose.staging.yml logs backend | grep -i migration
```

### Проверка состояния БД

```bash
# Список таблиц
docker-compose -f docker-compose.staging.yml exec db psql -U asia -d asia_crm_staging -c "\dt"

# Статус миграций
docker-compose -f docker-compose.staging.yml exec db psql -U asia -d asia_crm_staging -c "SELECT * FROM alembic_version;"
```

## 🎯 Результат

✅ **Полностью автоматизированная система миграций**
- Автоматическое применение при запуске контейнера
- Ожидание готовности базы данных
- Подробное логирование процесса
- Удобные инструменты управления

✅ **Готова к продакшену**
- Безопасные миграции с транзакциями
- Возможность отката изменений
- Мониторинг и логирование
- Документация и best practices

✅ **Интегрирована с Docker**
- Entrypoint скрипт для автоматизации
- Переменные окружения для конфигурации
- Health checks и мониторинг

## 🚀 Следующие шаги

1. **Настройка amoCRM интеграции** - добавить реальные токены
2. **Создание дополнительных API endpoints** - расширить функциональность
3. **Настройка мониторинга** - добавить метрики и алерты
4. **Деплой в продакшен** - настроить CI/CD pipeline

---

**Система автоматических миграций готова к использованию! 🎉**
