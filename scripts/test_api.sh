#!/bin/bash

# APEX Asia Property Exchange - API Testing Script
# Тестирование всех API endpoints

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

log_test() {
    echo -e "${PURPLE}[TEST]${NC} $1"
}

# Настройки
API_BASE_URL=${1:-"http://localhost:8001"}
WAIT_TIME=${2:-5}

# Проверка доступности curl
check_curl() {
    if ! command -v curl &> /dev/null; then
        log_error "curl не установлен!"
        exit 1
    fi
    log_success "curl готов к работе"
}

# Ожидание запуска API
wait_for_api() {
    log_info "Ожидаем запуска API сервера..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$API_BASE_URL/health" > /dev/null 2>&1; then
            log_success "API сервер готов!"
            return 0
        fi
        
        log_info "Попытка $attempt/$max_attempts - API не готов, ждем..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "API сервер не запустился за отведенное время"
    return 1
}

# Тест health check
test_health() {
    log_test "Тестируем Health Check endpoint..."
    
    local response=$(curl -s "$API_BASE_URL/health")
    local status=$(echo "$response" | jq -r '.status' 2>/dev/null || echo "unknown")
    
    if [ "$status" = "healthy" ]; then
        log_success "Health Check: ✅ $status"
        echo "Response: $response"
    else
        log_error "Health Check: ❌ $status"
        echo "Response: $response"
    fi
}

# Тест корневого endpoint
test_root() {
    log_test "Тестируем корневой endpoint..."
    
    local response=$(curl -s "$API_BASE_URL/")
    local message=$(echo "$response" | jq -r '.message' 2>/dev/null || echo "unknown")
    
    if [ "$message" = "APEX Asia Property Exchange API" ]; then
        log_success "Root endpoint: ✅ $message"
        echo "Response: $response"
    else
        log_error "Root endpoint: ❌ $message"
        echo "Response: $response"
    fi
}

# Тест API документации
test_docs() {
    log_test "Тестируем API документацию..."
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/docs")
    
    if [ "$response" = "200" ]; then
        log_success "API Docs: ✅ доступны (HTTP $response)"
        echo "URL: $API_BASE_URL/docs"
    else
        log_warning "API Docs: ⚠️ HTTP $response"
    fi
}

# Тест webhooks endpoint
test_webhooks() {
    log_test "Тестируем Webhooks endpoint..."
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/api/webhooks")
    
    if [ "$response" = "200" ] || [ "$response" = "405" ]; then
        log_success "Webhooks endpoint: ✅ доступен (HTTP $response)"
    else
        log_warning "Webhooks endpoint: ⚠️ HTTP $response"
    fi
}

# Тест auth endpoint
test_auth() {
    log_test "Тестируем Auth endpoint..."
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/api/auth")
    
    if [ "$response" = "200" ] || [ "$response" = "405" ]; then
        log_success "Auth endpoint: ✅ доступен (HTTP $response)"
    else
        log_warning "Auth endpoint: ⚠️ HTTP $response"
    fi
}

# Тест leads endpoint
test_leads() {
    log_test "Тестируем Leads endpoint..."
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/api/leads")
    
    if [ "$response" = "200" ] || [ "$response" = "405" ]; then
        log_success "Leads endpoint: ✅ доступен (HTTP $response)"
    else
        log_warning "Leads endpoint: ⚠️ HTTP $response"
    fi
}

# Тест analytics endpoint
test_analytics() {
    log_test "Тестируем Analytics endpoint..."
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/api/analytics")
    
    if [ "$response" = "200" ] || [ "$response" = "405" ]; then
        log_success "Analytics endpoint: ✅ доступен (HTTP $response)"
    else
        log_warning "Analytics endpoint: ⚠️ HTTP $response"
    fi
}

# Тест notifications endpoint
test_notifications() {
    log_test "Тестируем Notifications endpoint..."
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/api/notifications")
    
    if [ "$response" = "200" ] || [ "$response" = "405" ]; then
        log_success "Notifications endpoint: ✅ доступен (HTTP $response)"
    else
        log_warning "Notifications endpoint: ⚠️ HTTP $response"
    fi
}

# Тест amoCRM webhook
test_amocrm_webhook() {
    log_test "Тестируем amoCRM webhook..."
    
    # Создаем тестовые данные для webhook
    local webhook_data='{
        "leads": {
            "add": [{
                "id": 12345,
                "name": "Test Lead",
                "status_id": 1,
                "price": 100000,
                "created_at": 1234567890
            }]
        }
    }'
    
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "X-AmoCRM-Signature: test-signature" \
        -d "$webhook_data" \
        -o /dev/null -w "%{http_code}" \
        "$API_BASE_URL/api/webhooks/amocrm")
    
    if [ "$response" = "200" ] || [ "$response" = "201" ]; then
        log_success "amoCRM webhook: ✅ обработан (HTTP $response)"
    else
        log_warning "amoCRM webhook: ⚠️ HTTP $response"
    fi
}

# Тест создания лида
test_create_lead() {
    log_test "Тестируем создание лида..."
    
    local lead_data='{
        "name": "Test Lead API",
        "email": "test@example.com",
        "phone": "+1234567890",
        "source": "api_test",
        "description": "Test lead created via API"
    }'
    
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$lead_data" \
        "$API_BASE_URL/api/leads/")
    
    local status=$(echo "$response" | jq -r '.status' 2>/dev/null || echo "unknown")
    
    if [ "$status" = "success" ] || [ "$status" = "created" ]; then
        log_success "Create Lead: ✅ $status"
        echo "Response: $response"
    else
        log_warning "Create Lead: ⚠️ $status"
        echo "Response: $response"
    fi
}

# Тест получения лидов
test_get_leads() {
    log_test "Тестируем получение списка лидов..."
    
    local response=$(curl -s "$API_BASE_URL/api/leads/")
    local status=$(echo "$response" | jq -r '.status' 2>/dev/null || echo "unknown")
    
    if [ "$status" = "success" ] || [ "$status" = "ok" ]; then
        log_success "Get Leads: ✅ $status"
        echo "Response: $response"
    else
        log_warning "Get Leads: ⚠️ $status"
        echo "Response: $response"
    fi
}

# Тест аналитики
test_analytics_data() {
    log_test "Тестируем аналитику..."
    
    local response=$(curl -s "$API_BASE_URL/api/analytics/overview")
    local status=$(echo "$response" | jq -r '.status' 2>/dev/null || echo "unknown")
    
    if [ "$status" = "success" ] || [ "$status" = "ok" ]; then
        log_success "Analytics: ✅ $status"
        echo "Response: $response"
    else
        log_warning "Analytics: ⚠️ $status"
        echo "Response: $response"
    fi
}

# Основная функция тестирования
main() {
    echo "🧪 APEX Asia Property Exchange - API Testing"
    echo "============================================"
    echo
    
    log_info "API Base URL: $API_BASE_URL"
    log_info "Wait Time: $WAIT_TIME seconds"
    echo
    
    # Проверки
    check_curl
    
    # Ожидание API
    if ! wait_for_api; then
        log_error "Не удалось дождаться запуска API"
        exit 1
    fi
    
    echo
    log_info "Начинаем тестирование API endpoints..."
    echo
    
    # Базовые тесты
    test_health
    echo
    
    test_root
    echo
    
    test_docs
    echo
    
    # API endpoints тесты
    test_webhooks
    test_auth
    test_leads
    test_analytics
    test_notifications
    echo
    
    # Функциональные тесты
    test_amocrm_webhook
    echo
    
    test_create_lead
    echo
    
    test_get_leads
    echo
    
    test_analytics_data
    echo
    
    # Итоговый отчет
    echo "============================================"
    log_success "Тестирование API завершено!"
    echo
    log_info "Полезные ссылки:"
    echo "  • API Docs: $API_BASE_URL/docs"
    echo "  • Health Check: $API_BASE_URL/health"
    echo "  • Swagger UI: $API_BASE_URL/docs"
    echo "  • ReDoc: $API_BASE_URL/redoc"
    echo
}

# Обработка аргументов
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "Использование: $0 [API_BASE_URL] [WAIT_TIME]"
        echo
        echo "Аргументы:"
        echo "  API_BASE_URL  - Базовый URL API (по умолчанию: http://localhost:8001)"
        echo "  WAIT_TIME     - Время ожидания запуска API в секундах (по умолчанию: 5)"
        echo
        echo "Примеры:"
        echo "  $0                                    # Тест с настройками по умолчанию"
        echo "  $0 http://localhost:8001 10          # Кастомный URL и время ожидания"
        echo "  $0 http://staging.apex-asia.com      # Тест staging окружения"
        ;;
    *)
        main
        ;;
esac
