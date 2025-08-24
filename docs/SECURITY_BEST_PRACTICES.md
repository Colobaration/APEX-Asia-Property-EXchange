# 🔐 Лучшие практики безопасности для APEX Asia Property Exchange

## 🎯 Обзор

Этот документ описывает лучшие практики управления секретами и переменными окружения для разных сред развертывания.

## 📋 Классификация переменных

### 🔴 Критические секреты (всегда используйте Docker Secrets)
- `SECRET_KEY` - секретный ключ приложения
- `JWT_SECRET` - секрет для JWT токенов
- `AMOCRM_CLIENT_SECRET` - секрет AmoCRM
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `WHATSAPP_API_KEY` - ключ WhatsApp API
- `EMAIL_PASSWORD` - пароль email сервера

### 🟡 Важные переменные (используйте Docker Secrets в production)
- `AMOCRM_CLIENT_ID` - ID клиента AmoCRM
- `AMOCRM_REDIRECT_URI` - URI перенаправления AmoCRM
- `AMOCRM_SUBDOMAIN` - поддомен AmoCRM
- `TELEGRAM_CHAT_ID` - ID чата Telegram
- `EMAIL_USERNAME` - имя пользователя email
- `EMAIL_FROM` - адрес отправителя email

### 🟢 Обычные переменные (можно хранить в docker-compose)
- `ENVIRONMENT` - окружение (development/staging/production)
- `DEBUG` - режим отладки
- `LOG_LEVEL` - уровень логирования
- `DATABASE_URL` - URL базы данных
- `REDIS_URL` - URL Redis
- `ALLOWED_HOSTS_RAW` - разрешенные хосты
- `CORS_ORIGINS_RAW` - CORS origins

## 🐳 Docker Secrets (рекомендуется для production)

### Преимущества
- ✅ Секреты не попадают в логи
- ✅ Секреты не сохраняются в образах
- ✅ Централизованное управление
- ✅ Шифрование в состоянии покоя
- ✅ Ротация секретов

### Использование

#### 1. Создание секретов
```bash
# Из файла .env
./scripts/manage-secrets.sh create-from-file .env.production

# Интерактивно
./scripts/manage-secrets.sh interactive

# Просмотр секретов
./scripts/manage-secrets.sh list
```

#### 2. В docker-compose.yml
```yaml
services:
  backend:
    secrets:
      - secret_key
      - jwt_secret
      - amocrm_client_id
      - amocrm_client_secret
    environment:
      - ENVIRONMENT=production
      # Обычные переменные

secrets:
  secret_key:
    external: true
  jwt_secret:
    external: true
```

#### 3. В приложении
```python
# Секреты доступны как файлы в /run/secrets/
import os

def get_secret(secret_name: str) -> str:
    secret_file = f"/run/secrets/{secret_name}"
    if os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            return f.read().strip()
    return os.getenv(secret_name, "")
```

## 🌍 Окружения

### Development
```bash
# Используйте .env файлы
cp env.example .env.development
# Отредактируйте .env.development
docker-compose -f docker-compose.yml up
```

### Staging
```bash
# Используйте переменные окружения с fallback
docker-compose -f docker-compose.staging.yml up
```

### Production
```bash
# 1. Создайте секреты
./scripts/manage-secrets.sh interactive

# 2. Запустите с секретами
docker-compose -f docker-compose.production.yml up
```

## 🔧 Настройка интеграций

### AmoCRM
1. Зарегистрируйте приложение в AmoCRM
2. Получите `CLIENT_ID` и `CLIENT_SECRET`
3. Настройте `REDIRECT_URI`
4. Укажите `SUBDOMAIN`

```bash
# Создайте секреты
echo "your-amocrm-client-id" | docker secret create amocrm_client_id -
echo "your-amocrm-client-secret" | docker secret create amocrm_client_secret -
```

### Telegram
1. Создайте бота через @BotFather
2. Получите токен бота
3. Получите ID чата

```bash
# Создайте секреты
echo "your-telegram-bot-token" | docker secret create telegram_bot_token -
echo "your-chat-id" | docker secret create telegram_chat_id -
```

### WhatsApp Business API
1. Зарегистрируйтесь в WhatsApp Business API
2. Получите API ключ
3. Настройте webhook

```bash
# Создайте секреты
echo "your-whatsapp-api-key" | docker secret create whatsapp_api_key -
```

### Email (SMTP)
1. Настройте SMTP сервер
2. Создайте приложение-пароль (для Gmail)
3. Настройте отправителя

```bash
# Создайте секреты
echo "your-email-password" | docker secret create email_password -
echo "your-email-username" | docker secret create email_username -
```

## 🛡️ Дополнительные меры безопасности

### 1. Ротация секретов
```bash
# Обновление секрета
echo "new-secret-value" | docker secret create secret_key_new -
# Обновите docker-compose.yml
# Перезапустите сервисы
docker secret rm secret_key_old
```

### 2. Мониторинг
```bash
# Проверка использования секретов
docker secret ls
docker service ls
```

### 3. Резервное копирование
```bash
# Экспорт секретов (только для backup)
docker secret inspect secret_name
```

### 4. Логирование
- Не логируйте секреты
- Используйте маскирование в логах
- Настройте алерты на подозрительную активность

## 🚨 Важные предупреждения

### ❌ Никогда не делайте:
- Не коммитьте секреты в git
- Не используйте одинаковые секреты в разных окружениях
- Не передавайте секреты через URL параметры
- Не логируйте секреты
- Не используйте слабые пароли

### ✅ Всегда делайте:
- Используйте Docker Secrets в production
- Регулярно ротируйте секреты
- Используйте сильные пароли
- Ограничивайте доступ к секретам
- Мониторьте использование секретов

## 📚 Полезные ссылки

- [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/)
- [AmoCRM API Documentation](https://www.amocrm.ru/developers)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [SMTP Security Best Practices](https://tools.ietf.org/html/rfc8314)

## 🔄 Обновление секретов

### Автоматическое обновление
```bash
#!/bin/bash
# Скрипт для автоматической ротации секретов

# 1. Создайте новые секреты
./scripts/manage-secrets.sh interactive

# 2. Обновите docker-compose.yml
# 3. Перезапустите сервисы
docker-compose -f docker-compose.production.yml up -d

# 4. Удалите старые секреты
./scripts/manage-secrets.sh remove-all
```

---
*Документ обновлен: $(date)*
