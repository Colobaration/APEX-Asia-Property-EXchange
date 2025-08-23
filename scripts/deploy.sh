#!/bin/bash

# Скрипт для деплоя APEX Asia Property Exchange
# Использование: ./deploy.sh [staging|production] [version]

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

# Проверка наличия kubectl
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl не установлен"
    exit 1
fi

# Проверка подключения к кластеру
if ! kubectl cluster-info &> /dev/null; then
    log_error "Не удается подключиться к Kubernetes кластеру"
    exit 1
fi

# Установка переменных окружения
export NAMESPACE=$ENVIRONMENT
export IMAGE_TAG=$VERSION
export REGISTRY="ghcr.io"
export IMAGE_NAME="$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/')"

log_info "Namespace: $NAMESPACE"
log_info "Registry: $REGISTRY"
log_info "Image: $IMAGE_NAME"

# Создание namespace если не существует
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Применение конфигураций
log_info "Применяем ConfigMap и Secrets..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Деплой backend
log_info "Деплоим backend..."
envsubst < k8s/backend-deployment.yaml | kubectl apply -f -
kubectl apply -f k8s/backend-service.yaml

# Деплой frontend
log_info "Деплоим frontend..."
envsubst < k8s/frontend-deployment.yaml | kubectl apply -f -
kubectl apply -f k8s/frontend-service.yaml

# Применение Ingress
log_info "Применяем Ingress..."
envsubst < k8s/ingress.yaml | kubectl apply -f -

# Ожидание готовности деплойментов
log_info "Ожидаем готовности деплойментов..."
kubectl rollout status deployment/backend -n $NAMESPACE --timeout=300s
kubectl rollout status deployment/frontend -n $NAMESPACE --timeout=300s

# Проверка здоровья сервисов
log_info "Проверяем здоровье сервисов..."
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

# Проверка endpoints
log_info "Проверяем endpoints..."
kubectl get endpoints -n $NAMESPACE

log_info "Деплой завершен успешно!"
log_info "Backend доступен по адресу: api.$ENVIRONMENT.yourdomain.com"
log_info "Frontend доступен по адресу: $ENVIRONMENT.yourdomain.com"

# Уведомление в Slack (если настроено)
if [ ! -z "$SLACK_WEBHOOK" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"✅ Деплой $ENVIRONMENT завершен успешно! Версия: $VERSION\"}" \
        $SLACK_WEBHOOK
fi
