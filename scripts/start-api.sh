#!/bin/bash

# APEX Asia Property Exchange - Full Stack Startup Script
# Автоматический запуск полного стека приложения

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функции для вывода
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_service() {
    echo -e "${PURPLE}[SERVICE]${NC} $1"
}

# Определение окружения
ENVIRONMENT=${1:-development}
COMPOSE_FILE="docker-compose.yml"

case $ENVIRONMENT in
    "staging")
        COMPOSE_FILE="docker-compose.staging.yml"
        ENV_FILE=".env.staging"
        ;;
    "production")
        COMPOSE_FILE="docker-compose.prod.yml"
        ENV_FILE=".env.production"
        ;;
    "local")
        COMPOSE_FILE="docker-compose.local.yml"
        ENV_FILE=".env"
        ;;
    *)
        COMPOSE_FILE="docker-compose.yml"
        ENV_FILE=".env"
        ;;
esac

# Проверка наличия .env файла
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Файл $ENV_FILE не найден!"
        log_info "Создайте файл $ENV_FILE на основе env.example"
        exit 1
    fi
    log_success "Файл $ENV_FILE найден"
}

# Проверка Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker не установлен!"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker не запущен!"
        exit 1
    fi
    
    log_success "Docker готов к работе"
}

# Проверка Docker Compose
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose не установлен!"
        exit 1
    fi
    log_success "Docker Compose готов к работе"
}

# Остановка существующих контейнеров
stop_existing_containers() {
    log_info "Останавливаем существующие контейнеры..."
    docker-compose -f $COMPOSE_FILE down --remove-orphans || true
    log_success "Существующие контейнеры остановлены"
}

# Запуск сервисов
start_services() {
    log_info "Запускаем полный стек сервисов..."
    log_service "Окружение: $ENVIRONMENT"
    log_service "Compose файл: $COMPOSE_FILE"
    
    docker-compose -f $COMPOSE_FILE up -d
    
    log_info "Ожидаем запуска сервисов..."
    sleep 15
}

# Проверка статуса сервисов
check_services_status() {
    log_info "Проверяем статус всех сервисов..."
    
    # Проверка базы данных
    if docker-compose -f $COMPOSE_FILE exec -T db pg_isready -U asia > /dev/null 2>&1; then
        log_success "База данных PostgreSQL готова"
    else
        log_error "База данных PostgreSQL не готова"
        return 1
    fi
    
    # Проверка Redis
    if docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis готов"
    else
        log_error "Redis не готов"
        return 1
    fi
    
    # Проверка API сервера
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "API сервер готов"
            break
        fi
        
        log_info "Ожидаем готовности API сервера... (попытка $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "API сервер не запустился за отведенное время"
        return 1
    fi
    
    # Проверка Frontend
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            log_success "Frontend готов"
            break
        fi
        
        log_info "Ожидаем готовности Frontend... (попытка $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_warning "Frontend не запустился за отведенное время"
    fi
    
    # Проверка Metabase (если есть)
    if docker-compose -f $COMPOSE_FILE ps | grep -q metabase; then
        attempt=1
        while [ $attempt -le 20 ]; do
            if curl -f http://localhost:3001 > /dev/null 2>&1; then
                log_success "Metabase готов"
                break
            fi
            
            log_info "Ожидаем готовности Metabase... (попытка $attempt/20)"
            sleep 5
            attempt=$((attempt + 1))
        done
        
        if [ $attempt -gt 20 ]; then
            log_warning "Metabase не запустился за отведенное время"
        fi
    fi
    
    return 0
}

# Показать информацию о endpoints
show_endpoints_info() {
    log_info "=== Информация о сервисах ==="
    echo
    echo "🌐 Frontend:"
    echo "   • Web App: http://localhost:3000"
    echo
    echo "🔧 Backend API:"
    echo "   • API Docs: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/health"
    echo "   • Root: http://localhost:8000/"
    echo
    echo "🔗 API Endpoints:"
    echo "   • Webhooks: http://localhost:8000/api/webhooks"
    echo "   • Auth: http://localhost:8000/api/auth"
    echo "   • Leads: http://localhost:8000/api/leads"
    echo "   • Analytics: http://localhost:8000/api/analytics"
    echo "   • Notifications: http://localhost:8000/api/notifications"
    echo
    echo "📊 Аналитика:"
    echo "   • Metabase: http://localhost:3001"
    echo
    echo "🗄️  База данных:"
    echo "   • PostgreSQL: localhost:${DB_PORT:-5432}"
    echo "   • Redis: localhost:${REDIS_PORT:-6379}"
    echo
    echo "🌍 Прокси:"
    echo "   • Nginx: http://localhost:${NGINX_PORT:-80}"
    echo
    echo "📊 Мониторинг:"
    echo "   • Логи всех сервисов: docker-compose -f $COMPOSE_FILE logs -f"
    echo "   • Логи backend: docker-compose -f $COMPOSE_FILE logs -f backend"
    echo "   • Логи frontend: docker-compose -f $COMPOSE_FILE logs -f frontend"
    echo
}

# Показать логи
show_logs() {
    log_info "Показываем логи всех сервисов..."
    docker-compose -f $COMPOSE_FILE logs -f
}

# Показать логи конкретного сервиса
show_service_logs() {
    local service=$1
    log_info "Показываем логи сервиса: $service"
    docker-compose -f $COMPOSE_FILE logs -f $service
}

# Основная функция
main() {
    echo "🚀 APEX Asia Property Exchange - Full Stack Startup"
    echo "=================================================="
    echo
    
    # Проверки
    check_env_file
    check_docker
    check_docker_compose
    
    # Остановка существующих контейнеров
    stop_existing_containers
    
    # Запуск сервисов
    start_services
    
    # Проверка статуса
    if check_services_status; then
        log_success "Все сервисы успешно запущены!"
        echo
        show_endpoints_info
        
        # Спрашиваем пользователя о показе логов
        echo
        read -p "Показать логи всех сервисов? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            show_logs
        fi
    else
        log_error "Ошибка при запуске сервисов"
        log_info "Проверьте логи: docker-compose -f $COMPOSE_FILE logs"
        exit 1
    fi
}

# Обработка аргументов командной строки
case "${2:-}" in
    "stop")
        log_info "Останавливаем сервисы..."
        docker-compose -f $COMPOSE_FILE down
        log_success "Сервисы остановлены"
        ;;
    "restart")
        log_info "Перезапускаем сервисы..."
        docker-compose -f $COMPOSE_FILE restart
        log_success "Сервисы перезапущены"
        ;;
    "logs")
        show_logs
        ;;
    "backend")
        show_service_logs "backend"
        ;;
    "frontend")
        show_service_logs "frontend"
        ;;
    "db")
        show_service_logs "db"
        ;;
    "redis")
        show_service_logs "redis"
        ;;
    "metabase")
        show_service_logs "metabase"
        ;;
    "status")
        docker-compose -f $COMPOSE_FILE ps
        ;;
    "help"|"-h"|"--help")
        echo "Использование: $0 [окружение] [команда]"
        echo
        echo "Окружения:"
        echo "  development (по умолчанию) - docker-compose.yml"
        echo "  staging                    - docker-compose.staging.yml"
        echo "  production                 - docker-compose.prod.yml"
        echo "  local                      - docker-compose.local.yml"
        echo
        echo "Команды:"
        echo "  (без аргументов) - Запустить полный стек"
        echo "  stop             - Остановить сервисы"
        echo "  restart          - Перезапустить сервисы"
        echo "  logs             - Показать логи всех сервисов"
        echo "  backend          - Показать логи backend"
        echo "  frontend         - Показать логи frontend"
        echo "  db               - Показать логи базы данных"
        echo "  redis            - Показать логи Redis"
        echo "  metabase         - Показать логи Metabase"
        echo "  status           - Показать статус контейнеров"
        echo "  help             - Показать эту справку"
        echo
        echo "Примеры:"
        echo "  $0                    # Запустить development окружение"
        echo "  $0 staging            # Запустить staging окружение"
        echo "  $0 staging logs       # Показать логи staging"
        echo "  $0 production stop    # Остановить production"
        ;;
    *)
        main
        ;;
esac
