# 🐳 Руководство по развертыванию в Portainer

## 📋 Проблема и решение

### ❌ Проблема:
```
Failed to deploy a stack: failed to resolve services environment: 
env file /data/compose/29/.env not found: stat /data/compose/29/.env: no such file or directory
```

### ✅ Решение:
Созданы файлы переменных окружения для каждого окружения:
- `development.env` - для development окружения
- `staging.env` - для staging окружения

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

## 📁 Файлы переменных окружения

### development.env
```bash
# Основные настройки
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# База данных
POSTGRES_USER=asia
POSTGRES_PASSWORD=asia
POSTGRES_DB=asia_crm_dev
DATABASE_URL=postgresql://asia:asia@db:5432/asia_crm_dev

# Безопасность
SECRET_KEY=your-dev-secret-key-change-in-production-2025
JWT_SECRET=your-dev-jwt-secret-change-in-production-2025

# И другие переменные...
```

### staging.env
```bash
# Основные настройки
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=WARNING

# База данных
POSTGRES_USER=asia
POSTGRES_PASSWORD=asia
POSTGRES_DB=asia_crm_staging
DATABASE_URL=postgresql://asia:asia@db:5432/asia_crm_staging

# Безопасность
SECRET_KEY=your-staging-secret-key-change-in-production-2025
JWT_SECRET=your-staging-jwt-secret-change-in-production-2025

# И другие переменные...
```

## 🔧 Конфигурация в docker-compose

### env_file секция:
```yaml
services:
  backend:
    env_file:
      - development.env  # или staging.env
    environment:
      - ENVIRONMENT=development
      # Дополнительные переменные...
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
**Решение**: Убедитесь, что файлы `development.env` и `staging.env` находятся в корне проекта.

### 2. Конфликт портов
**Решение**: Используйте разные порты для разных окружений (уже настроено).

### 3. Проблемы с базой данных
**Решение**: Проверьте переменные окружения в файлах `.env`.

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

## ✅ Готово к развертыванию!

Теперь Portainer сможет корректно развернуть оба окружения без ошибок с файлами `.env`.
