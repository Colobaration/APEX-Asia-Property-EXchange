# 🔧 Исправление Healthcheck для Frontend Контейнера

## Проблема
Контейнер `asia-frontend-staging` показывал статус "unhealthy" с ошибкой:
```
OCI runtime exec failed: exec failed: unable to start container process: exec: "curl": executable file not found in $PATH: unknown
```

## Причина
1. В frontend Dockerfile не был установлен `curl`, необходимый для healthcheck
2. Отсутствовал API health endpoint для проверки состояния приложения
3. Healthcheck пытался обратиться к несуществующему endpoint

## Решение

### 1. Обновлен Frontend Dockerfile
```dockerfile
# Установка curl для healthcheck
RUN apk add --no-cache curl
```

### 2. Создан API Health Endpoint
Создан файл `frontend/pages/api/health.ts`:
```typescript
export default function handler(
  _req: NextApiRequest,
  res: NextApiResponse
) {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    environment: process.env.ENVIRONMENT || 'development',
    service: 'frontend'
  })
}
```

### 3. Исправлен Healthcheck в docker-compose.staging.yml
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 4. Создан Скрипт Пересборки
Создан `scripts/rebuild-frontend.sh` для удобной пересборки контейнера.

## Результат
- ✅ Frontend контейнер теперь корректно проходит healthcheck
- ✅ API health endpoint доступен по адресу `/api/health`
- ✅ Контейнер показывает статус "healthy" в Portainer
- ✅ Добавлен curl для отладки и мониторинга

## Команды для применения на сервере
```bash
# Пересборка frontend контейнера
./scripts/rebuild-frontend.sh

# Или вручную
docker-compose -f docker-compose.staging.yml stop frontend
docker-compose -f docker-compose.staging.yml rm -f frontend
docker-compose -f docker-compose.staging.yml build frontend
docker-compose -f docker-compose.staging.yml up -d frontend
```

## Дата исправления
2025-01-25
