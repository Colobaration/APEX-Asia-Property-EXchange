#!/bin/bash

echo "🚀 Запуск APEX Webhook Server..."

# Проверяем, что Docker запущен
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker не запущен. Запустите Docker Desktop и попробуйте снова."
    exit 1
fi

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose -f docker-compose.staging.yml down

# Собираем и запускаем
echo "🔨 Собираем и запускаем сервисы..."
docker-compose -f docker-compose.staging.yml up --build -d

# Ждем немного
echo "⏳ Ждем запуска сервисов..."
sleep 10

# Проверяем статус
echo "📊 Статус сервисов:"
docker-compose -f docker-compose.staging.yml ps

echo ""
echo "✅ Webhook сервер запущен!"
echo ""
echo "📋 Доступные endpoints:"
echo "   • Health check: http://localhost:8001/health"
echo "   • Webhook test: http://localhost:8001/api/webhooks/amo/test"
echo "   • Webhook health: http://localhost:8001/api/webhooks/amo/health"
echo "   • Main webhook: http://localhost:8001/api/webhooks/amo"
echo ""
echo "🔧 Для amoCRM настройте webhook URL:"
echo "   http://your-server:8001/api/webhooks/amo"
echo ""
echo "📝 Логи: docker-compose -f docker-compose.staging.yml logs -f"
echo "🛑 Остановка: docker-compose -f docker-compose.staging.yml down"
