# Миграции базы данных - APEX Asia Property Exchange

## Обзор

Система миграций базы данных использует **Alembic** для управления схемой PostgreSQL. Все изменения в структуре базы данных должны выполняться через миграции.

## Автоматические миграции

### При запуске контейнера

При запуске backend контейнера автоматически выполняются следующие шаги:

1. **Ожидание готовности БД** - скрипт ждет, пока PostgreSQL станет доступным
2. **Проверка миграций** - проверяется текущая версия схемы
3. **Выполнение миграций** - применяются все новые миграции
4. **Запуск приложения** - стартует FastAPI сервер

### Переменные окружения

```bash
# Включить автоматическую инициализацию БД
INIT_DB=true

# URL базы данных
DATABASE_URL=postgresql://asia:asia@db:5432/asia_crm_staging

# Окружение
ENVIRONMENT=staging
```

## Ручное управление миграциями

### Использование Makefile

```bash
# Показать справку
make help

# Выполнить все миграции
make migrate

# Создать новую миграцию
make migrate-create MESSAGE="Add user preferences table"

# Показать статус миграций
make migrate-status

# Откатить последнюю миграцию
make migrate-down

# Сбросить все миграции (ОПАСНО!)
make migrate-reset

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

### Использование Alembic напрямую

```bash
# Выполнить миграции
alembic -c alembic.ini upgrade head

# Создать миграцию
alembic -c alembic.ini revision --autogenerate -m "Add new column"

# Показать текущую версию
alembic -c alembic.ini current

# Показать историю
alembic -c alembic.ini history
```

## Docker команды

```bash
# Выполнить миграции в контейнере
make docker-migrate

# Инициализировать БД в контейнере
make docker-init-db

# Или напрямую
docker-compose -f ../docker-compose.staging.yml exec backend python scripts/run_migrations.py
```

## Структура миграций

```
backend/
├── alembic/
│   ├── versions/           # Файлы миграций
│   │   ├── 196dfdb50f6c_initial_migration.py
│   │   └── 20240101000000_add_amocrm_tokens.py
│   ├── env.py             # Конфигурация окружения
│   └── script.py.mako     # Шаблон для миграций
├── alembic.ini            # Конфигурация Alembic
└── scripts/
    ├── run_migrations.py  # Скрипт выполнения миграций
    ├── init_db.py         # Скрипт инициализации БД
    └── create_migration.py # Скрипт создания миграций
```

## Создание новой миграции

### 1. Измените модели

Отредактируйте файлы в `app/models/` для изменения структуры БД.

### 2. Создайте миграцию

```bash
make migrate-create MESSAGE="Add user preferences"
```

### 3. Проверьте миграцию

Откройте созданный файл в `alembic/versions/` и проверьте SQL команды.

### 4. Примените миграцию

```bash
make migrate
```

## Best Practices

### ✅ Правильно

- Всегда создавайте миграции для изменений схемы
- Используйте описательные сообщения для миграций
- Тестируйте миграции на staging перед продакшеном
- Делайте backup перед применением миграций в продакшене
- Используйте транзакции для сложных миграций

### ❌ Неправильно

- Изменять схему БД напрямую без миграций
- Удалять файлы миграций из истории
- Применять миграции без тестирования
- Игнорировать ошибки при выполнении миграций

## Troubleshooting

### Ошибка "database does not exist"

```bash
# Создайте базу данных
make init-db
```

### Ошибка "relation does not exist"

```bash
# Выполните миграции
make migrate
```

### Конфликт миграций

```bash
# Проверьте статус
make migrate-status

# При необходимости откатитесь
make migrate-down
```

### Проблемы с подключением к БД

```bash
# Проверьте переменные окружения
echo $DATABASE_URL

# Проверьте доступность БД
docker-compose -f ../docker-compose.staging.yml exec db psql -U asia -d asia_crm_staging -c "SELECT 1"
```

## Мониторинг

### Логи миграций

```bash
# Просмотр логов backend
docker-compose -f ../docker-compose.staging.yml logs backend

# Фильтр по миграциям
docker-compose -f ../docker-compose.staging.yml logs backend | grep -i migration
```

### Проверка состояния БД

```bash
# Список таблиц
docker-compose -f ../docker-compose.staging.yml exec db psql -U asia -d asia_crm_staging -c "\dt"

# Статус миграций
docker-compose -f ../docker-compose.staging.yml exec db psql -U asia -d asia_crm_staging -c "SELECT * FROM alembic_version;"
```

## Продакшен

### Безопасное применение миграций

```bash
# Проверка плана миграции
make prod-migrate
```

### Backup перед миграцией

```bash
# Создание backup
docker-compose -f ../docker-compose.staging.yml exec db pg_dump -U asia asia_crm_staging > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Rollback план

```bash
# Откат миграции
make migrate-down
```
