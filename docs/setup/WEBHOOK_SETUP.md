# 🚀 Настройка APEX Webhook Server

## 📋 Что это такое?

APEX Webhook Server - это сервер для приема webhook'ов от amoCRM. Он обрабатывает события создания, обновления и удаления лидов и контактов.

## 🎯 Доступные endpoints

- **Health check**: `GET /health`
- **Webhook test**: `GET /api/webhooks/amo/test`
- **Webhook health**: `GET /api/webhooks/amo/health`
- **Main webhook**: `POST /api/webhooks/amo`

## 🚀 Способы запуска

### 1. Portainer (рекомендуется)

1. Откройте Portainer
2. Перейдите в **Stacks**
3. Нажмите **"Add stack"**
4. Заполните настройки:
   - **Name**: `apex-webhook-staging`
   - **Repository URL**: `https://github.com/Colobaration/APEX-Asia-Property-EXchange.git`
   - **Repository reference**: `refs/heads/develop`
   - **Compose path**: `docker-compose.staging.yml`
5. Нажмите **"Deploy the stack"**

### 2. Локально (для разработки)

```bash
# Запуск
./scripts/start-webhook.sh

# Или вручную
docker-compose -f docker-compose.staging.yml up --build -d

# Просмотр логов
docker-compose -f docker-compose.staging.yml logs -f

# Остановка
docker-compose -f docker-compose.staging.yml down
```

## 🔧 Настройка amoCRM

### 1. В amoCRM перейдите в настройки интеграций

### 2. Добавьте новый webhook:
- **URL**: `http://your-server:8001/api/webhooks/amo`
- **Метод**: POST
- **События**:
  - ✅ leads.add
  - ✅ leads.update
  - ✅ leads.delete
  - ✅ contacts.add
  - ✅ contacts.update

### 3. Настройте заголовки:
- `X-Client-UUID`: ваш UUID
- `X-Signature`: подпись (настраивается в amoCRM)
- `X-Account-ID`: ID аккаунта

## 📊 Тестирование

### 1. Проверка health check:
```bash
curl http://localhost:8001/health
```

### 2. Тест webhook endpoint:
```bash
curl http://localhost:8001/api/webhooks/amo/test
```

### 3. Тест webhook health:
```bash
curl http://localhost:8001/api/webhooks/amo/health
```

## 🗄️ База данных

Сервер автоматически создает таблицы при первом запуске:
- `leads` - таблица лидов
- `deals` - таблица сделок
- `amocrm_tokens` - токены amoCRM

## 📝 Логирование

Логи доступны через:
```bash
# Все сервисы
docker-compose -f docker-compose.staging.yml logs -f

# Только backend
docker-compose -f docker-compose.staging.yml logs -f backend

# Только база данных
docker-compose -f docker-compose.staging.yml logs -f db
```

## 🔍 Мониторинг

### Полезные команды:

```bash
# Статус сервисов
docker-compose -f docker-compose.staging.yml ps

# Использование ресурсов
docker stats

# Проверка подключения к БД
docker-compose -f docker-compose.staging.yml exec db psql -U asia -d asia_crm_staging -c "SELECT COUNT(*) FROM leads;"
```

## 🛠️ Устранение проблем

### 1. Сервер не запускается
- Проверьте, что Docker запущен
- Проверьте логи: `docker-compose -f docker-compose.staging.yml logs`

### 2. Webhook не принимается
- Проверьте URL в amoCRM
- Проверьте заголовки запроса
- Проверьте логи backend

### 3. Проблемы с БД
- Проверьте подключение: `docker-compose -f docker-compose.staging.yml exec db psql -U asia -d asia_crm_staging`
- Проверьте логи БД: `docker-compose -f docker-compose.staging.yml logs db`

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи
2. Убедитесь, что все сервисы запущены
3. Проверьте настройки amoCRM
4. Обратитесь к документации проекта
