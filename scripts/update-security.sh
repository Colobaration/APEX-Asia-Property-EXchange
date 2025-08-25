#!/bin/bash

# 🛡️ Security Update Script for APEX Asia Property Exchange
# Автоматическое обновление пакетов безопасности

set -e  # Остановка при ошибке

echo "🔍 Starting security update process..."

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

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    error "Python3 не найден"
    exit 1
fi

# Проверка наличия pip
if ! command -v pip &> /dev/null; then
    error "pip не найден"
    exit 1
fi

# Проверка наличия npm
if ! command -v npm &> /dev/null; then
    warning "npm не найден, пропускаем frontend обновления"
    SKIP_FRONTEND=true
fi

log "Обновление pip..."
pip install --upgrade pip
success "pip обновлен"

log "Обновление критически важных Python пакетов..."
pip install --upgrade requests certifi urllib3 httpx
success "Критически важные пакеты обновлены"

log "Обновление инструментов разработки..."
pip install --upgrade black isort flake8 mypy
success "Инструменты разработки обновлены"

# Обновление frontend зависимостей
if [ "$SKIP_FRONTEND" != "true" ]; then
    log "Обновление frontend зависимостей..."
    cd frontend
    npm audit fix
    success "Frontend зависимости обновлены"
    cd ..
fi

# Проверка уязвимостей
log "Проверка уязвимостей Python..."
if command -v safety &> /dev/null; then
    safety check || warning "Найдены уязвимости (см. отчет выше)"
else
    warning "safety не установлен, устанавливаем..."
    pip install safety
    safety check || warning "Найдены уязвимости (см. отчет выше)"
fi

# Обновление requirements.txt
log "Обновление requirements.txt..."
cd backend
pip freeze > requirements-current.txt
success "Текущие зависимости сохранены в requirements-current.txt"

# Создание отчета
log "Создание отчета безопасности..."
cat > security-report.txt << EOF
# Отчет безопасности APEX Asia Property Exchange
# Дата: $(date)

## Обновленные пакеты:
$(pip list --outdated | grep -E "(requests|certifi|urllib3|httpx|black|isort|flake8|mypy)" || echo "Все пакеты актуальны")

## Проверка уязвимостей:
$(safety check --json 2>/dev/null || echo "Ошибка при проверке уязвимостей")

## Рекомендации:
1. Регулярно обновлять зависимости
2. Мониторить уязвимости через GitHub Dependabot
3. Рассмотреть переход на PyJWT вместо python-jose
4. Настроить автоматическое сканирование в CI/CD

EOF

success "Отчет безопасности создан: security-report.txt"

cd ..

log "Обновление завершено!"
success "Все критические обновления безопасности применены"

echo ""
echo "📊 Следующие шаги:"
echo "1. Проверить security-report.txt"
echo "2. Протестировать приложение"
echo "3. Создать коммит с обновлениями"
echo "4. Запустить CI/CD для проверки"
echo ""

log "Security update completed successfully! 🛡️"
