# 🐳 Руководство по развертыванию в Portainer

## 📋 Проблема и решение

### ❌ Проблема:
```
Failed to deploy a stack: failed to resolve services environment: 
env file /data/compose/32/.env not found: stat /data/compose/32/.env: no such file or directory
```

### ✅ Решение:
Убрали зависимость от файлов `.env` и перенесли все переменные окружения прямо в `docker-compose.yml` файлы.

## 🚀 Инструкция по развертыванию

### 1. Development окружение

#### В Portainer:
1. **Stacks** → **Add stack**
2. **Name**: `apex-development`
3. **Build method**: **Web editor**
4. **Copy content** из `docker-compose.yml`
5. **Deploy the stack**

#### Локально:
```bash
# Запуск development окружения
docker-compose up -d

# Проверка статуса
docker-compose ps

# Логи
docker-compose logs [service]
```

### 2. Staging окружение

#### В Portainer:
1. **Stacks** → **Add stack**
2. **Name**: `apex-staging`
3. **Build method**: **Web editor**
4. **Copy content** из `docker-compose.staging.yml`
5. **Deploy the stack**

#### Локально:
```bash
# Запуск staging окружения
docker-compose -f docker-compose.staging.yml up -d

# Проверка статуса
docker-compose -f docker-compose.staging.yml ps

# Логи
docker-compose -f docker-compose.staging.yml logs [service]
```

## 🔧 Конфигурация переменных окружения

### Development (docker-compose.yml):
```yaml
environment:
  - ENVIRONMENT=development
  - LOG_LEVEL=DEBUG
  - INIT_DB=true
  - RUN_MIGRATIONS=true
  - DATABASE_URL=postgresql://asia:asia@db:5432/asia_crm_dev
  - SECRET_KEY=your-dev-secret-key-change-in-production
  - JWT_SECRET=your-dev-jwt-secret-change-in-production
  - CORS_ORIGINS_RAW=http://localhost:3001,https://dev.apex-asia.com
```

### Staging (docker-compose.staging.yml):
```yaml
environment:
  - ENVIRONMENT=staging
  - LOG_LEVEL=WARNING
  - INIT_DB=false
  - RUN_MIGRATIONS=false
  - DATABASE_URL=postgresql://asia:asia@db:5432/asia_crm_staging
  - SECRET_KEY=your-staging-secret-key-change-in-production
  - JWT_SECRET=your-staging-jwt-secret-change-in-production
  - CORS_ORIGINS_RAW=http://localhost:3000,https://staging.apex-asia.com
```

## 🌐 Доступ к сервисам

### Development:
- **Backend API**: `http://localhost:8000`
- **Frontend**: `http://localhost:3001`
- **Admin Panel**: `http://localhost:8003`
- **Database**: `localhost:5432`
- **Redis**: `localhost:6379`

### Staging:
- **Backend API**: `http://localhost:8001`
- **Frontend**: `http://localhost:3000`
- **Admin Panel**: `http://localhost:8002`
- **Database**: `localhost:5433`
- **Redis**: `localhost:6380`

## 🔍 Проверка работоспособности

### Health Checks:
```bash
# Backend
curl -f http://localhost:8000/health
curl -f http://localhost:8001/health

# Frontend
curl -f http://localhost:3001/api/health
curl -f http://localhost:3000/api/health

# Admin Panel
curl -f http://localhost:8003/admin/
curl -f http://localhost:8002/admin/
```

### Проверка контейнеров:
```bash
# Статус всех контейнеров
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Логи сервиса
docker-compose logs [service]
```

## 🛠️ Устранение неполадок

### 1. Файл .env не найден
**Решение**: ✅ Исправлено - все переменные окружения теперь в docker-compose файлах.

### 2. Конфликт портов
**Решение**: Используйте разные порты для разных окружений (уже настроено).

### 3. Проблемы с базой данных
**Решение**: Проверьте переменные окружения в docker-compose файлах.

### 4. Проблемы с сетью
**Решение**: Убедитесь, что сети созданы корректно.

## 📝 Важные замечания

### 🔐 Безопасность:
- **Замените секретные ключи** в production
- **Используйте Docker Secrets** для чувствительных данных
- **Не коммитьте** реальные секреты в Git

### 🔧 Настройка:
- **Проверьте порты** перед запуском
- **Убедитесь в наличии** всех файлов
- **Проверьте права доступа** к файлам

### 📊 Мониторинг:
- **Настройте логирование** для production
- **Мониторьте ресурсы** контейнеров
- **Проверяйте health checks** регулярно

## 🔄 Обновление переменных окружения

### Для изменения переменных:
1. Отредактируйте соответствующий `docker-compose.yml` файл
2. Обновите stack в Portainer
3. Или пересоберите локально: `docker-compose up -d --build`

### Переменные для настройки:
```yaml
# Основные
- ENVIRONMENT=development|staging|production
- LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
- DEBUG=true|false

# База данных
- DATABASE_URL=postgresql://user:pass@host:port/db
- POSTGRES_USER=asia
- POSTGRES_PASSWORD=asia
- POSTGRES_DB=asia_crm_dev|asia_crm_staging

# Безопасность
- SECRET_KEY=your-secret-key
- JWT_SECRET=your-jwt-secret

# Интеграции
- AMOCRM_CLIENT_ID=your-client-id
- AMOCRM_CLIENT_SECRET=your-client-secret
- TELEGRAM_BOT_TOKEN=your-bot-token
- WHATSAPP_API_KEY=your-api-key
```

## ✅ Готово к развертыванию!

Теперь Portainer сможет корректно развернуть оба окружения без ошибок с файлами `.env`. Все переменные окружения встроены в docker-compose файлы.
