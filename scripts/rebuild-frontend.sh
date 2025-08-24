#!/bin/bash

echo "🔧 Пересборка frontend контейнера..."

# Остановка и удаление существующего контейнера
docker-compose -f docker-compose.staging.yml stop frontend
docker-compose -f docker-compose.staging.yml rm -f frontend

# Удаление старого образа
docker rmi apex-dev-frontend 2>/dev/null || true

# Пересборка образа
docker-compose -f docker-compose.staging.yml build frontend

# Запуск нового контейнера
docker-compose -f docker-compose.staging.yml up -d frontend

echo "✅ Frontend контейнер пересобран и запущен"
echo "📊 Проверка статуса..."
docker-compose -f docker-compose.staging.yml ps frontend

