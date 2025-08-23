# 🚀 Простой CI/CD Pipeline для APEX Asia Property Exchange

Упрощенная система автоматического деплоя с использованием GitHub Actions и Docker Compose (без Kubernetes).

## 📋 Быстрый старт

### 1. Настройка GitHub Secrets

Добавьте следующие секреты в настройках репозитория (`Settings` → `Secrets and variables` → `Actions`):

```bash
# Slack уведомления (опционально)
SLACK_WEBHOOK=<slack-webhook-url>

# Домены
DOMAIN=<your-domain.com>
```

### 2. Создание Environments

Создайте environments в настройках репозитория:
- `staging` - для тестового окружения
- `production` - для продакшена

### 3. Настройка сервера

Убедитесь, что на сервере установлены:
- Docker
- Docker Compose
- Git

## 🔄 Workflow процессы

### Автоматический деплой

| Действие | Ветка | Результат |
|----------|-------|-----------|
| Push в `develop` | develop | Деплой в staging |
| Push в `main` | main | Деплой в production |
| Pull Request | любая | Только тестирование |

### Ручной деплой

```bash
# Деплой в staging
./scripts/deploy-simple.sh staging

# Деплой в production
./scripts/deploy-simple.sh production

# Деплой конкретной версии
./scripts/deploy-simple.sh production v1.2.3
```

## 🛠 Команды Makefile

```bash
# Полная проверка перед деплоем
make pre-deploy

# Тестирование
make test
make test-backend
make test-frontend

# Линтинг
make lint
make lint-backend
make lint-frontend

# Сборка Docker образов
make docker-build
make docker-push

# Деплой
make deploy-staging
make deploy-production

# Управление окружениями
make dev              # Запуск development
make staging          # Запуск staging
make production       # Запуск production

# Мониторинг
make status           # Статус всех сервисов
make logs             # Логи development
make logs-staging     # Логи staging
make logs-production  # Логи production

# Безопасность
make security-scan

# Резервное копирование
make backup           # Резервная копия БД
make backup-staging   # Резервная копия staging БД
```

## 📁 Структура файлов

```
.github/
├── workflows/
│   ├── ci-cd-simple.yml      # Упрощенный CI/CD pipeline
│   └── security-scan.yml     # Сканирование безопасности

docker-compose.yml            # Development окружение
docker-compose.staging.yml    # Staging окружение
docker-compose.prod.yml       # Production окружение

nginx/
├── nginx.conf               # Конфигурация для production
└── nginx-staging.conf       # Конфигурация для staging

scripts/
└── deploy-simple.sh         # Скрипт деплоя

docs/
└── ci-cd-setup.md          # Подробная документация
```

## 🔒 Безопасность

### Сканирование уязвимостей

- **Python**: `safety` для проверки зависимостей
- **Node.js**: `npm audit` для проверки пакетов
- **Docker**: `Trivy` для сканирования образов
- **Автоматическое**: каждую неделю в понедельник

### Секреты

- Переменные окружения в `.env` файлах
- GitHub Secrets для CI/CD
- SSL сертификаты для production

## 📊 Мониторинг

### Health Checks

- Backend: `GET /health`
- Frontend: `GET /`

### Логи

```bash
# Логи development
make logs

# Логи staging
make logs-staging

# Логи production
make logs-production

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Статус сервисов

```bash
# Статус всех окружений
make status

# Статус development
docker-compose ps

# Статус staging
docker-compose -f docker-compose.staging.yml ps

# Статус production
docker-compose -f docker-compose.prod.yml ps
```

## 🔄 Откат деплоя

### Ручной откат

```bash
# Остановить текущие контейнеры
docker-compose -f docker-compose.prod.yml down

# Запустить предыдущую версию
TAG=v1.2.2 docker-compose -f docker-compose.prod.yml up -d

# Или использовать скрипт
./scripts/deploy-simple.sh production v1.2.2
```

### Автоматический откат

1. Перейдите в GitHub Actions
2. Выберите "Rollback Deployment"
3. Выберите окружение и версию
4. Нажмите "Run workflow"

## 🚨 Troubleshooting

### Частые проблемы

1. **Ошибка сборки образа**
   ```bash
   # Проверьте Dockerfile
   docker build -t test ./backend
   
   # Проверьте зависимости
   make install
   ```

2. **Ошибка деплоя**
   ```bash
   # Проверьте Docker и Docker Compose
   docker --version
   docker-compose --version
   
   # Проверьте доступ к registry
   docker pull ghcr.io/your-repo/backend:latest
   ```

3. **Сервис не отвечает**
   ```bash
   # Проверьте статус контейнеров
   make status
   
   # Проверьте логи
   make logs
   
   # Проверьте health checks
   curl http://localhost:8000/health
   curl http://localhost:3000/
   ```

### Полезные команды

```bash
# Подключение к контейнеру
docker exec -it asia-backend bash
docker exec -it asia-frontend bash

# Просмотр переменных окружения
docker exec asia-backend env

# Перезапуск сервиса
docker-compose restart backend
docker-compose restart frontend

# Очистка
make clean-all
```

## 📈 Метрики и аналитика

### Code Coverage

- Backend: генерируется в `backend/htmlcov/`
- Frontend: генерируется в `frontend/coverage/`
- Отправляется в Codecov

### Время деплоя

- Staging: ~3-5 минут
- Production: ~5-8 минут

### Уведомления

- Slack уведомления о статусе деплоя
- GitHub Actions статус в репозитории

## 🔧 Настройка для новых проектов

1. Скопируйте файлы CI/CD в ваш проект
2. Обновите переменные в `.github/variables.env`
3. Настройте GitHub Secrets
4. Обновите домены в конфигурациях
5. Протестируйте pipeline

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи GitHub Actions
2. Проверьте статус Docker контейнеров
3. Обратитесь к документации в `docs/ci-cd-setup.md`
4. Создайте issue в репозитории

## 🆚 Сравнение с Kubernetes версией

| Функция | Простая версия | Kubernetes версия |
|---------|----------------|-------------------|
| Сложность настройки | 🟢 Низкая | 🔴 Высокая |
| Масштабируемость | 🟡 Средняя | 🟢 Высокая |
| Отказоустойчивость | 🟡 Средняя | 🟢 Высокая |
| Мониторинг | 🟢 Простой | 🟢 Продвинутый |
| Обновления | 🟢 Простые | 🟢 Продвинутые |
| Требования к серверу | 🟢 Минимальные | 🔴 Высокие |

---

**Удачного деплоя! 🚀**
