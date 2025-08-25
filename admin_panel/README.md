# APEX Asia Property Exchange - Админ-панель

Комплексная админ-панель для управления системой APEX Asia Property Exchange с возможностью управления лендингами, API интеграциями, ключами и логами.

## 🚀 Возможности

### 📊 Управление лендингами
- Создание/редактирование/удаление лендингов
- Настройка UTM меток
- Просмотр статистики (посетители, конверсии)
- Управление темами и конфигурацией
- Мониторинг статуса

### 🔌 API интеграции
- Настройка различных типов интеграций (AmoCRM, WhatsApp, Telegram, Email, SMS)
- Управление API ключами и токенами
- Мониторинг статуса интеграций
- Настройка webhook'ов
- Автоматическая синхронизация

### 📈 Аналитика
- Дашборд с ключевыми метриками
- Графики конверсий по лендингам
- Анализ источников трафика
- UTM аналитика
- Экспорт отчетов

### 📝 Системные логи
- Просмотр всех системных логов
- Фильтрация по уровню, типу, источнику
- Поиск по сообщениям
- Экспорт логов
- Мониторинг ошибок

### 🔔 Уведомления
- Управление шаблонами уведомлений
- Логи отправки
- Статистика доставки

## 🛠 Технологический стек

- **Backend**: Django 4.2.7 + PostgreSQL
- **Frontend**: Django Admin + Bootstrap 5
- **Контейнеризация**: Docker + Docker Compose
- **Кэширование**: Redis
- **Прокси**: Nginx
- **Дополнительные сервисы**: Portainer, Adminer

## 📦 Установка и запуск

### Локальная разработка

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd admin_panel
```

2. **Создание виртуального окружения**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

4. **Настройка переменных окружения**
```bash
cp env.example .env
# Отредактируйте .env файл под ваши нужды
```

5. **Применение миграций**
```bash
python manage.py migrate
```

6. **Создание суперпользователя**
```bash
python manage.py createsuperuser
```

7. **Запуск сервера разработки**
```bash
python manage.py runserver 8001
```

### Docker развертывание

Админ-панель интегрирована в основную инфраструктуру APEX. Для запуска:

1. **Запуск всех сервисов (включая админ-панель)**
```bash
# Из корневой директории проекта
docker-compose -f docker-compose.staging.yml up -d
```

2. **Запуск только админ-панели**
```bash
# Из директории admin_panel
make up
```

3. **Применение миграций**
```bash
docker-compose -f docker-compose.staging.yml exec admin-panel python manage.py migrate
```

4. **Создание суперпользователя**
```bash
docker-compose -f docker-compose.staging.yml exec admin-panel python manage.py createsuperuser
```

## 🎯 Использование Makefile

```bash
# Показать справку
make help

# Установить зависимости
make install

# Запустить тесты
make test

# Запустить сервер разработки
make run

# Собрать и запустить Docker контейнеры
make build
make up

# Показать логи
make logs

# Остановить сервисы
make down

# Очистить Docker ресурсы
make clean

# Мониторинг системы
make monitor

# Проверить здоровье системы
make health
```

## 🌐 Доступные сервисы

После запуска будут доступны следующие сервисы:

- **Админ-панель**: http://localhost:8002/admin/
- **API Backend**: http://localhost:8001/
- **Frontend**: http://localhost:3000/
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6380

### В продакшн окружении:
- **Админ-панель**: https://admin.staging.apex-asia.com
- **API Backend**: https://api.staging.apex-asia.com
- **Frontend**: https://staging.apex-asia.com

## 📊 Структура проекта

```
admin_panel/
├── apex_admin/          # Основные настройки Django
├── landings/           # Управление лендингами
├── integrations/       # API интеграции
├── analytics/          # Аналитика и метрики
├── logs/              # Системные логи
├── templates/         # HTML шаблоны
├── static/            # CSS, JS, изображения
├── media/             # Загружаемые файлы
├── logs/              # Логи приложения
├── nginx/             # Конфигурация Nginx
├── requirements.txt   # Python зависимости
├── Dockerfile         # Docker образ
├── docker-compose.yml # Docker Compose
├── manage.py          # Django management
├── Makefile           # Команды управления
└── README.md          # Документация
```

## 🔧 Конфигурация

### Переменные окружения

Основные переменные окружения (см. `env.example`):

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=apex_admin_db
POSTGRES_USER=apex_admin_user
POSTGRES_PASSWORD=apex_admin_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# External APIs
AMOCRM_CLIENT_ID=your-amocrm-client-id
AMOCRM_CLIENT_SECRET=your-amocrm-client-secret
WHATSAPP_API_KEY=your-whatsapp-api-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
make test

# Запуск конкретного теста
python manage.py test tests.AdminPanelTestCase.test_admin_login

# Запуск тестов с покрытием
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📈 Мониторинг и логирование

### Логи

- **Django логи**: `logs/django.log`
- **Nginx логи**: доступны через Docker
- **Системные логи**: в админ-панели

### Мониторинг

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Логи в реальном времени
docker-compose logs -f
```

## 🔒 Безопасность

- HTTPS для всех соединений
- Валидация входных данных
- Защита от SQL инъекций
- Rate limiting
- Логирование действий пользователей
- Защита API ключей

## 🚀 Деплой в продакшн

1. **Подготовка сервера**
```bash
# Установка Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Настройка SSL сертификатов**
```bash
# Создание самоподписанных сертификатов для тестирования
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem
```

3. **Запуск в продакшн режиме**
```bash
make deploy
```

## 🤝 Разработка

### Добавление новых моделей

1. Создайте модель в соответствующем приложении
2. Создайте миграцию: `python manage.py makemigrations`
3. Примените миграцию: `python manage.py migrate`
4. Добавьте модель в админку
5. Напишите тесты

### Добавление новых API интеграций

1. Создайте новый тип интеграции в `integrations/models.py`
2. Добавьте логику в `integrations/admin.py`
3. Создайте соответствующие тесты
4. Обновите документацию

## 📞 Поддержка

- **Документация**: см. папку `docs/`
- **Issues**: создавайте issues в репозитории
- **Email**: admin@apex-asia.com

## 📄 Лицензия

MIT License - см. файл `LICENSE` для деталей.

## 🔄 Обновления

```bash
# Обновление кода
git pull origin main

# Обновление зависимостей
pip install -r requirements.txt --upgrade

# Применение миграций
python manage.py migrate

# Перезапуск сервисов
docker-compose restart
```

---

**APEX Asia Property Exchange** - Комплексная система управления недвижимостью в Азии
