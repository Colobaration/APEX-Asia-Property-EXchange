#!/bin/bash
set -e

echo "🚀 APEX Asia Property Exchange - Backend Entrypoint"
echo "=================================================="

# Функция для логирования
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Функция для ожидания готовности базы данных
wait_for_db() {
    log "⏳ Ожидание готовности базы данных..."
    
    local max_retries=30
    local retry_interval=2
    local attempt=1
    
    while [ $attempt -le $max_retries ]; do
        if python -c "
import os
import sys
sys.path.append('/app')
from scripts.run_migrations import wait_for_database
import os
db_url = os.getenv('DATABASE_URL')
if wait_for_database(db_url):
    exit(0)
else:
    exit(1)
" 2>/dev/null; then
            log "✅ База данных готова!"
            return 0
        else
            log "⚠️  Попытка $attempt/$max_retries: База данных недоступна"
            if [ $attempt -lt $max_retries ]; then
                sleep $retry_interval
            fi
            attempt=$((attempt + 1))
        fi
    done
    
    log "❌ База данных не стала доступной в течение ожидаемого времени"
    return 1
}

# Функция для запуска миграций
run_migrations() {
    log "🔄 Запуск миграций базы данных..."
    
    if python /app/scripts/run_migrations.py; then
        log "✅ Миграции выполнены успешно!"
        return 0
    else
        log "❌ Ошибка при выполнении миграций"
        return 1
    fi
}

# Функция для инициализации базы данных
init_database() {
    log "🗄️  Инициализация базы данных..."
    
    if python /app/scripts/init_db.py; then
        log "✅ База данных инициализирована успешно!"
        return 0
    else
        log "❌ Ошибка при инициализации базы данных"
        return 1
    fi
}

# Основная логика
main() {
    log "📋 Проверка переменных окружения..."
    
    # Проверяем обязательные переменные
    if [ -z "$DATABASE_URL" ]; then
        log "❌ DATABASE_URL не установлена"
        exit 1
    fi
    
    if [ -z "$ENVIRONMENT" ]; then
        log "⚠️  ENVIRONMENT не установлена, используем 'development'"
        export ENVIRONMENT=development
    fi
    
    log "🌍 Окружение: $ENVIRONMENT"
    log "🗄️  База данных: $DATABASE_URL"
    
    # Ждем готовности базы данных
    if ! wait_for_db; then
        exit 1
    fi
    
    # Запускаем миграции
    if ! run_migrations; then
        exit 1
    fi
    
    # Если это первичный запуск, инициализируем базу данных
    if [ "$INIT_DB" = "true" ]; then
        if ! init_database; then
            log "⚠️  Предупреждение: Не удалось инициализировать базу данных"
        fi
    fi
    
    log "🎉 Инициализация завершена успешно!"
    log "🚀 Запуск FastAPI приложения..."
    
    # Запускаем FastAPI приложение
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Запускаем основную функцию
main "$@"
