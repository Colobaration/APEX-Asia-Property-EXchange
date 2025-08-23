#!/bin/bash

# Упрощенный скрипт деплоя APEX Asia Property Exchange
# Использование: ./deploy-simple.sh [staging|production] [version]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функции для логирования
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка аргументов
if [ $# -lt 1 ]; then
    log_error "Использование: $0 [staging|production] [version]"
    exit 1
fi

ENVIRONMENT=$1
VERSION=${2:-$(git rev-parse --short HEAD)}

# Проверка окружения
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log_error "Окружение должно быть 'staging' или 'production'"
    exit 1
fi

log_info "Начинаем деплой в окружение: $ENVIRONMENT"
log_info "Версия: $VERSION"

# Установка переменных окружения
export TAG=$VERSION
export REGISTRY="ghcr.io"
export IMAGE_NAME="$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/')"

log_info "Registry: $REGISTRY"
log_info "Image: $IMAGE_NAME"

# Проверка наличия Docker и Docker Compose
if ! command -v docker &> /dev/null; then
    log_error "Docker не установлен"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose не установлен"
    exit 1
fi

# Проверка подключения к Docker registry
log_info "Проверяем подключение к registry..."
if ! docker pull $REGISTRY/$IMAGE_NAME-backend:$VERSION &> /dev/null; then
    log_error "Не удается получить образ backend:$VERSION"
    exit 1
fi

if ! docker pull $REGISTRY/$IMAGE_NAME-frontend:$VERSION &> /dev/null; then
    log_error "Не удается получить образ frontend:$VERSION"
    exit 1
fi

# Создание директорий
log_info "Создаем необходимые директории..."
mkdir -p logs/nginx
mkdir -p backups
mkdir -p nginx/ssl

# Остановка существующих контейнеров
log_info "Останавливаем существующие контейнеры..."
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose -f docker-compose.prod.yml down || true
else
    docker-compose -f docker-compose.staging.yml down || true
fi

# Очистка неиспользуемых образов
log_info "Очищаем неиспользуемые образы..."
docker image prune -f

# Запуск новых контейнеров
log_info "Запускаем новые контейнеры..."
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose -f docker-compose.prod.yml up -d
else
    docker-compose -f docker-compose.staging.yml up -d
fi

# Ожидание готовности сервисов
log_info "Ожидаем готовности сервисов..."
sleep 30

# Проверка здоровья сервисов
log_info "Проверяем здоровье сервисов..."

if [ "$ENVIRONMENT" = "production" ]; then
    # Проверка backend
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_info "✅ Backend готов"
    else
        log_error "❌ Backend не отвечает"
        exit 1
    fi

    # Проверка frontend
    if curl -f http://localhost:3000 &> /dev/null; then
        log_info "✅ Frontend готов"
    else
        log_error "❌ Frontend не отвечает"
        exit 1
    fi

    # Проверка базы данных
    if docker exec asia-db-prod pg_isready -U asia -d asia_crm &> /dev/null; then
        log_info "✅ База данных готова"
    else
        log_error "❌ База данных не отвечает"
        exit 1
    fi
else
    # Проверка backend
    if curl -f http://localhost:8001/health &> /dev/null; then
        log_info "✅ Backend готов"
    else
        log_error "❌ Backend не отвечает"
        exit 1
    fi

    # Проверка frontend
    if curl -f http://localhost:3001 &> /dev/null; then
        log_info "✅ Frontend готов"
    else
        log_error "❌ Frontend не отвечает"
        exit 1
    fi

    # Проверка базы данных
    if docker exec asia-db-staging pg_isready -U asia -d asia_crm_staging &> /dev/null; then
        log_info "✅ База данных готова"
    else
        log_error "❌ База данных не отвечает"
        exit 1
    fi
fi

# Показать статус контейнеров
log_info "Статус контейнеров:"
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose -f docker-compose.prod.yml ps
else
    docker-compose -f docker-compose.staging.yml ps
fi

log_info "Деплой завершен успешно!"

if [ "$ENVIRONMENT" = "production" ]; then
    log_info "Backend доступен по адресу: http://localhost:8000"
    log_info "Frontend доступен по адресу: http://localhost:3000"
    log_info "База данных доступна на порту: 5432"
else
    log_info "Backend доступен по адресу: http://localhost:8001"
    log_info "Frontend доступен по адресу: http://localhost:3001"
    log_info "База данных доступна на порту: 5433"
fi

# Уведомление в Slack (если настроено)
if [ ! -z "$SLACK_WEBHOOK" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"✅ Деплой $ENVIRONMENT завершен успешно! Версия: $VERSION\"}" \
        $SLACK_WEBHOOK
fi
