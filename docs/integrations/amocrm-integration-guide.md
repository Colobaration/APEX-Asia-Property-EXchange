# 🚀 Руководство по интеграции с amoCRM

## 📋 Обзор

Данная интеграция позволяет автоматически создавать лидов в amoCRM, синхронизировать статусы и получать уведомления об изменениях через webhooks.

## 🎯 Возможности

- ✅ **OAuth2 авторизация** с amoCRM
- ✅ **Автоматическое создание контактов** и сделок
- ✅ **Синхронизация статусов** между системами
- ✅ **Webhook обработка** для real-time обновлений
- ✅ **UTM метки** для аналитики
- ✅ **Теги и кастомные поля**
- ✅ **Безопасное хранение токенов** в БД

## 🔧 Требования

### Системные требования
- Python 3.8+
- PostgreSQL
- FastAPI
- Docker (опционально)

### amoCRM требования
- Аккаунт amoCRM с правами администратора
- Доступ к API amoCRM
- Настроенные кастомные поля (см. ниже)

## 📝 Пошаговая настройка

### Шаг 1: Создание приложения в amoCRM

1. **Войдите в amoCRM** под администратором
2. **Перейдите в Настройки** → **Интеграции** → **Создать интеграцию**
3. **Заполните форму:**
   ```
   Название: Asia Deals CRM Integration
   Описание: Интеграция для автоматизации продаж недвижимости
   Тип: Веб-приложение
   Redirect URI: http://localhost:8000/api/auth/amo/callback
   ```
4. **Сохраните приложение** и получите:
   - Client ID
   - Client Secret

### Шаг 2: Настройка OAuth2 прав

В настройках приложения перейдите в раздел "OAuth2" и включите:

- ✅ **Контакты** (чтение, запись)
- ✅ **Сделки** (чтение, запись)
- ✅ **Компании** (чтение)
- ✅ **Воронки** (чтение)

### Шаг 3: Создание кастомных полей

#### Для контактов:
| Поле | ID | Тип | Обязательно |
|------|----|-----|-------------|
| Телефон | 123456 | Телефон | ✅ |
| Email | 123457 | Email | ❌ |

#### Для сделок:
| Поле | ID | Тип | Обязательно |
|------|----|-----|-------------|
| UTM Source | 123458 | Текст | ❌ |
| UTM Medium | 123459 | Текст | ❌ |
| UTM Campaign | 123460 | Текст | ❌ |
| UTM Content | 123461 | Текст | ❌ |
| UTM Term | 123462 | Текст | ❌ |
| Стоимость объекта | 123463 | Число | ❌ |
| Комиссия | 123464 | Число | ❌ |
| Объект | 123466 | Список | ❌ |
| Статус оплаты | 123467 | Список | ❌ |

### Шаг 4: Создание воронки "Asia Deals"

Создайте воронку с названием "Asia Deals" и статусами:

| Статус | ID | Название | Описание |
|--------|----|----------|----------|
| 1 | 1 | Новый лид | Первичный контакт |
| 2 | 2 | Первичный контакт | Звонок менеджера |
| 3 | 3 | Презентация | Показ объектов |
| 4 | 4 | Выбор объекта | Клиент выбрал недвижимость |
| 5 | 5 | Резервирование | Внесение депозита |
| 6 | 6 | Сделка | Закрытие сделки |
| 7 | 7 | Завершено | Успешная сделка |

### Шаг 5: Настройка webhooks

1. **Настройки** → **Интеграции** → **Webhooks**
2. **Добавьте webhook:**
   ```
   URL: http://your-domain.com/api/webhooks/amo
   События:
   - ✅ Создание лидов
   - ✅ Изменение лидов
   - ✅ Создание контактов
   - ✅ Изменение контактов
   ```

### Шаг 6: Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните:

```bash
# amoCRM Configuration
AMOCRM_CLIENT_ID=your_client_id_here
AMOCRM_CLIENT_SECRET=your_client_secret_here
AMOCRM_REDIRECT_URI=http://localhost:8000/api/auth/amo/callback
AMOCRM_DOMAIN=your-company.amocrm.ru
AMOCRM_REFRESH_TOKEN=your_refresh_token_here

# Database Configuration
DB_URL=postgresql://asia:asia@db:5432/asia_crm

# Frontend Configuration
FRONTEND_URL=http://localhost:3000
```

### Шаг 7: Запуск приложения

```bash
# Запуск с Docker
docker-compose up -d

# Или локально
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Шаг 8: Авторизация в amoCRM

1. **Откройте в браузере:** `http://localhost:8000/api/auth/amo`
2. **Авторизуйтесь в amoCRM**
3. **Скопируйте refresh token** из callback URL
4. **Добавьте в .env файл**

## 🧪 Тестирование интеграции

### Автоматическое тестирование

```bash
# Запуск тестов
python scripts/test_amocrm_integration.py
```

### Ручное тестирование

#### 1. Проверка статуса авторизации
```bash
curl -X GET http://localhost:8000/api/auth/amo/status
```

#### 2. Тест подключения
```bash
curl -X GET http://localhost:8000/api/auth/amo/test
```

#### 3. Создание тестового лида
```bash
curl -X POST http://localhost:8000/api/leads/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Тест Тестов",
    "phone": "+79001234567",
    "email": "test@example.com",
    "utm_source": "google",
    "utm_medium": "cpc",
    "utm_campaign": "asia_deals_test"
  }'
```

#### 4. Получение списка лидов
```bash
curl -X GET http://localhost:8000/api/leads/
```

#### 5. Обновление статуса лида
```bash
curl -X PUT http://localhost:8000/api/leads/1/status?status=contacted
```

## 📊 API Endpoints

### Авторизация
- `GET /api/auth/amo` - Начало OAuth2 авторизации
- `GET /api/auth/amo/callback` - Callback для получения токенов
- `GET /api/auth/amo/status` - Статус авторизации
- `POST /api/auth/amo/refresh` - Обновление токенов
- `POST /api/auth/amo/revoke` - Отзыв токенов
- `GET /api/auth/amo/test` - Тест подключения

### Лиды
- `POST /api/leads/` - Создание лида
- `GET /api/leads/` - Получение списка лидов
- `GET /api/leads/{id}` - Получение лида по ID
- `PUT /api/leads/{id}/status` - Обновление статуса лида
- `GET /api/leads/{id}/amo` - Информация о лиде из amoCRM

### Webhooks
- `POST /api/webhooks/amo` - Обработка webhook от amoCRM
- `GET /api/webhooks/amo/test` - Тест webhook endpoint

## 🔒 Безопасность

### Проверка подлинности webhook

Webhook от amoCRM проверяется с помощью HMAC подписи:

```python
def verify_webhook_signature(client_uuid, signature, account_id, client_secret):
    message = f"{client_uuid}|{account_id}"
    expected_signature = hmac.new(
        client_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
```

### Хранение токенов

Токены хранятся в БД с шифрованием и автоматическим обновлением:

- Access token обновляется автоматически при истечении
- Refresh token сохраняется для долгосрочного доступа
- Старые токены деактивируются при получении новых

## 🚨 Обработка ошибок

### Частые проблемы и решения

#### 1. "Invalid client_id"
**Причина:** Неправильный Client ID в .env файле
**Решение:** Проверьте правильность Client ID в настройках приложения amoCRM

#### 2. "Access token expired"
**Причина:** Истек access token
**Решение:** Токен обновится автоматически, или обновите refresh token

#### 3. "Field not found"
**Причина:** Кастомные поля не созданы в amoCRM
**Решение:** Создайте поля с указанными ID согласно таблице выше

#### 4. "Webhook not received"
**Причина:** Неправильный URL webhook или недоступность сервера
**Решение:** Проверьте URL webhook и доступность сервера

#### 5. "Database connection failed"
**Причина:** Проблемы с подключением к БД
**Решение:** Проверьте настройки БД и запустите миграции

### Логирование

Все операции логируются в файл `logs/app.log`:

```bash
# Просмотр логов
tail -f logs/app.log

# Поиск ошибок
grep "ERROR" logs/app.log
```

## 📈 Мониторинг

### Метрики для отслеживания

- Количество созданных лидов
- Время отклика API amoCRM
- Количество ошибок авторизации
- Статистика webhook событий

### Health check

```bash
curl -X GET http://localhost:8000/health
```

## 🔄 Обновления и поддержка

### Обновление интеграции

1. Остановите приложение
2. Обновите код
3. Запустите миграции БД
4. Перезапустите приложение

### Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs backend`
2. Проверьте статус: `http://localhost:8000/health`
3. Обратитесь к документации API: `/docs`
4. Создайте issue в репозитории

## 🎯 Следующие шаги

После успешной настройки интеграции:

1. **Настройте email воронки** (SMTP)
2. **Подключите WhatsApp API**
3. **Настройте аналитические дашборды**
4. **Проведите нагрузочное тестирование**
5. **Разверните в продакшн**

---

**Готово к интеграции!** 🚀

Интеграция настроена и готова к работе. Следуйте инструкциям выше для полной настройки.
