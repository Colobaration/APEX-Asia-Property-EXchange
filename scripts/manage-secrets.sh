#!/bin/bash

# 🔐 APEX Asia Property Exchange - Управление секретами
# ======================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверка наличия Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker не установлен"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker не запущен или нет прав доступа"
        exit 1
    fi
}

# Создание секрета
create_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if [ -z "$secret_value" ]; then
        warning "Секрет $secret_name пустой, пропускаем"
        return
    fi
    
    if docker secret ls | grep -q "$secret_name"; then
        warning "Секрет $secret_name уже существует, обновляем..."
        docker secret rm "$secret_name" > /dev/null 2>&1 || true
    fi
    
    echo "$secret_value" | docker secret create "$secret_name" - > /dev/null
    success "Секрет $secret_name создан"
}

# Создание всех секретов из файла
create_secrets_from_file() {
    local env_file=$1
    
    if [ ! -f "$env_file" ]; then
        error "Файл $env_file не найден"
        exit 1
    fi
    
    log "Создание секретов из файла $env_file..."
    
    # Читаем файл и создаем секреты
    while IFS='=' read -r key value; do
        # Пропускаем комментарии и пустые строки
        if [[ $key =~ ^#.*$ ]] || [[ -z $key ]]; then
            continue
        fi
        
        # Убираем пробелы
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        
        # Создаем секрет только для важных переменных
        case $key in
            SECRET_KEY|JWT_SECRET|AMOCRM_*|TELEGRAM_*|WHATSAPP_*|EMAIL_*)
                create_secret "${key,,}" "$value"
                ;;
            *)
                log "Пропускаем $key (не является секретом)"
                ;;
        esac
    done < "$env_file"
    
    success "Все секреты созданы"
}

# Удаление всех секретов
remove_all_secrets() {
    log "Удаление всех секретов..."
    
    local secrets=(
        "secret_key"
        "jwt_secret"
        "amocrm_client_id"
        "amocrm_client_secret"
        "amocrm_redirect_uri"
        "amocrm_subdomain"
        "telegram_bot_token"
        "telegram_chat_id"
        "whatsapp_api_url"
        "whatsapp_api_key"
        "email_smtp_host"
        "email_smtp_port"
        "email_username"
        "email_password"
        "email_from"
    )
    
    for secret in "${secrets[@]}"; do
        if docker secret ls | grep -q "$secret"; then
            docker secret rm "$secret" > /dev/null 2>&1
            success "Секрет $secret удален"
        else
            log "Секрет $secret не найден"
        fi
    done
}

# Просмотр списка секретов
list_secrets() {
    log "Список секретов:"
    docker secret ls
}

# Интерактивное создание секретов
interactive_create() {
    log "Интерактивное создание секретов..."
    
    echo
    echo "Введите значения для секретов (оставьте пустым для пропуска):"
    echo
    
    # Безопасность
    read -s -p "SECRET_KEY: " secret_key
    echo
    read -s -p "JWT_SECRET: " jwt_secret
    echo
    
    # AmoCRM
    read -p "AMOCRM_CLIENT_ID: " amocrm_client_id
    read -s -p "AMOCRM_CLIENT_SECRET: " amocrm_client_secret
    echo
    read -p "AMOCRM_REDIRECT_URI: " amocrm_redirect_uri
    read -p "AMOCRM_SUBDOMAIN: " amocrm_subdomain
    
    # Telegram
    read -s -p "TELEGRAM_BOT_TOKEN: " telegram_bot_token
    echo
    read -p "TELEGRAM_CHAT_ID: " telegram_chat_id
    
    # WhatsApp
    read -p "WHATSAPP_API_URL: " whatsapp_api_url
    read -s -p "WHATSAPP_API_KEY: " whatsapp_api_key
    echo
    
    # Email
    read -p "EMAIL_SMTP_HOST: " email_smtp_host
    read -p "EMAIL_SMTP_PORT: " email_smtp_port
    read -p "EMAIL_USERNAME: " email_username
    read -s -p "EMAIL_PASSWORD: " email_password
    echo
    read -p "EMAIL_FROM: " email_from
    
    # Создаем секреты
    create_secret "secret_key" "$secret_key"
    create_secret "jwt_secret" "$jwt_secret"
    create_secret "amocrm_client_id" "$amocrm_client_id"
    create_secret "amocrm_client_secret" "$amocrm_client_secret"
    create_secret "amocrm_redirect_uri" "$amocrm_redirect_uri"
    create_secret "amocrm_subdomain" "$amocrm_subdomain"
    create_secret "telegram_bot_token" "$telegram_bot_token"
    create_secret "telegram_chat_id" "$telegram_chat_id"
    create_secret "whatsapp_api_url" "$whatsapp_api_url"
    create_secret "whatsapp_api_key" "$whatsapp_api_key"
    create_secret "email_smtp_host" "$email_smtp_host"
    create_secret "email_smtp_port" "$email_smtp_port"
    create_secret "email_username" "$email_username"
    create_secret "email_password" "$email_password"
    create_secret "email_from" "$email_from"
}

# Показать справку
show_help() {
    echo "🔐 APEX Asia Property Exchange - Управление секретами"
    echo "====================================================="
    echo
    echo "Использование: $0 [КОМАНДА]"
    echo
    echo "Команды:"
    echo "  create-from-file FILE    Создать секреты из файла .env"
    echo "  interactive              Интерактивное создание секретов"
    echo "  remove-all               Удалить все секреты"
    echo "  list                     Показать список секретов"
    echo "  help                     Показать эту справку"
    echo
    echo "Примеры:"
    echo "  $0 create-from-file .env.production"
    echo "  $0 interactive"
    echo "  $0 list"
    echo
}

# Основная логика
main() {
    check_docker
    
    case "${1:-help}" in
        "create-from-file")
            if [ -z "$2" ]; then
                error "Укажите файл .env"
                exit 1
            fi
            create_secrets_from_file "$2"
            ;;
        "interactive")
            interactive_create
            ;;
        "remove-all")
            remove_all_secrets
            ;;
        "list")
            list_secrets
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Запуск скрипта
main "$@"
