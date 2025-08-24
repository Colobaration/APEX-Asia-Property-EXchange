# Portainer Setup для APEX Asia Property Exchange

## 🚀 Настройка Portainer для автоматического деплоя

### 📋 Предварительные требования

1. **Portainer установлен** и доступен по адресу `portainer.nodehub.ru`
2. **Git репозиторий** настроен в Portainer
3. **Docker Compose** файлы готовы в репозитории

### 🔧 Настройка Stack в Portainer

#### 1. Создание нового Stack

1. Откройте Portainer: `http://portainer.nodehub.ru`
2. Перейдите в раздел **Stacks**
3. Нажмите **"Add stack"**

#### 2. Настройка Git Repository

```
Name: apex-staging
Repository URL: https://github.com/Colobaration/APEX-Asia-Property-EXchange.git
Repository reference: devops
Compose path: docker-compose.staging.yml
```

#### 3. Настройка переменных окружения

В разделе **Environment variables** добавьте переменные из файла `portainer-staging.env`:

```bash
# Основные настройки
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Порты сервисов
BACKEND_PORT=8001
DB_PORT=5433
REDIS_PORT=6380
NGINX_PORT=80
NGINX_SSL_PORT=443
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# База данных
DB_USER=asia
DB_PASSWORD=your_secure_password_here
DB_NAME=asia_crm_staging

# Redis
REDIS_PASSWORD=your_redis_password_here

# Безопасность
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# amoCRM (заполните своими данными)
AMOCRM_CLIENT_ID=your_client_id
AMOCRM_CLIENT_SECRET=your_client_secret
AMOCRM_DOMAIN=your_domain.amocrm.ru
```

#### 4. Настройка GitOps

Включите **GitOps updates**:
- ✅ **GitOps updates**: ON
- **Mechanism**: Polling
- **Fetch interval**: 2m
- ✅ **Environment variables**: включено

### 🔄 Автоматическое обновление

После настройки Portainer будет:
- Проверять репозиторий каждые 2 минуты
- Автоматически обновлять stack при изменениях в `docker-compose.staging.yml`
- Перезапускать сервисы с новыми настройками

### 📊 Мониторинг сервисов

#### Доступные endpoints:

- **API Backend**: `http://your-server:8001`
  - Health Check: `http://your-server:8001/health`
  - API Docs: `http://your-server:8001/docs`
  - Webhooks: `http://your-server:8001/api/webhooks`

- **База данных**: `your-server:5433`
- **Redis**: `your-server:6380`
- **Nginx**: `http://your-server:80`
- **Prometheus**: `http://your-server:9090`
- **Grafana**: `http://your-server:3001`

### 🔧 Управление через Portainer

#### Просмотр логов:
1. Перейдите в **Containers**
2. Выберите контейнер (например, `asia-backend-staging`)
3. Нажмите **Logs**

#### Перезапуск сервисов:
1. В разделе **Stacks**
2. Выберите `apex-staging`
3. Нажмите **"Pull and redeploy"**

#### Обновление переменных:
1. Отредактируйте переменные в настройках stack
2. Нажмите **"Update the stack"**

### 🚨 Важные замечания

#### Безопасность:
- ✅ Все пароли должны быть сложными
- ✅ Используйте разные пароли для разных окружений
- ✅ Не коммитьте реальные пароли в Git

#### Мониторинг:
- ✅ Health checks настроены для всех сервисов
- ✅ Prometheus и Grafana для метрик
- ✅ Логи сохраняются в volumes

#### Обновления:
- ⚠️ Изменения в Git перезапишут локальные настройки
- ⚠️ Всегда тестируйте изменения в staging перед production

### 🔄 Workflow разработки

1. **Разработка**: Работайте в ветке `devops`
2. **Тестирование**: Изменения автоматически деплоятся в staging
3. **Production**: После тестирования мержите в `main`

### 📝 Полезные команды

```bash
# Проверка статуса сервисов
curl http://your-server:8001/health

# Проверка логов backend
docker logs asia-backend-staging

# Проверка подключения к БД
docker exec asia-db-staging pg_isready -U asia

# Проверка Redis
docker exec asia-redis-staging redis-cli ping
```

### 🆘 Troubleshooting

#### Сервис не запускается:
1. Проверьте логи в Portainer
2. Убедитесь, что все переменные окружения заполнены
3. Проверьте доступность портов

#### GitOps не работает:
1. Проверьте настройки Git repository
2. Убедитесь, что файл `docker-compose.staging.yml` существует
3. Проверьте права доступа к репозиторию

#### Проблемы с базой данных:
1. Проверьте переменные `DB_*`
2. Убедитесь, что volume `pgdata_staging` создан
3. Проверьте логи контейнера `asia-db-staging`

### 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в Portainer
2. Убедитесь, что все переменные окружения корректны
3. Проверьте доступность всех сервисов
4. Обратитесь к документации API: `http://your-server:8001/docs`
