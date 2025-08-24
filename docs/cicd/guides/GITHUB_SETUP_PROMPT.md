# 🚀 Промт для настройки CI/CD в GitHub

## 📋 Информация о проекте

### Основные данные:
- **Название проекта**: APEX Asia Property Exchange
- **GitHub репозиторий**: https://github.com/Colobaration/APEX-Asia-Property-EXchange
- **Владелец**: Colobaration
- **Пользователь**: 5iNeX (daniil113122@gmail.com)
- **Текущая ветка**: develop (с примененными изменениями CI/CD)

### Архитектура проекта:
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js (React 18)
- **База данных**: PostgreSQL 15
- **Кэш**: Redis 7
- **Прокси**: Nginx
- **Контейнеризация**: Docker + Docker Compose

### Структура проекта:
```
APEX-Asia-Property-EXchange/
├── backend/                 # FastAPI приложение
├── frontend/               # Next.js приложение
├── .github/workflows/      # GitHub Actions
├── docker-compose.yml      # Development
├── docker-compose.staging.yml  # Staging
├── docker-compose.prod.yml     # Production
├── nginx/                  # Nginx конфигурации
├── scripts/                # Скрипты деплоя
└── docs/                   # Документация
```

## 🎯 Цель настройки

Настроить полную систему CI/CD для автоматического деплоя проекта с использованием GitHub Actions и Docker Compose (без Kubernetes).

## 📁 Созданные файлы CI/CD

### GitHub Actions Workflows:
1. **`.github/workflows/ci-cd-simple.yml`** - основной CI/CD pipeline
2. **`.github/workflows/security-scan.yml`** - сканирование безопасности
3. **`.github/workflows/ci-cd.yml`** - полная версия с Kubernetes (опционально)
4. **`.github/workflows/deploy-kubernetes.yml`** - деплой в Kubernetes (опционально)
5. **`.github/workflows/rollback.yml`** - откат деплоя

### Docker Compose конфигурации:
1. **`docker-compose.prod.yml`** - production окружение
2. **`docker-compose.staging.yml`** - staging окружение

### Скрипты:
1. **`scripts/deploy-simple.sh`** - упрощенный скрипт деплоя
2. **`scripts/deploy.sh`** - скрипт для Kubernetes (опционально)

### Nginx конфигурации:
1. **`nginx/nginx.conf`** - для production
2. **`nginx/nginx-staging.conf`** - для staging

### Документация:
1. **`README-CI-CD-SIMPLE.md`** - документация по простой версии
2. **`README-CI-CD.md`** - документация по полной версии
3. **`docs/ci-cd-setup.md`** - подробная настройка

## 🔧 Что нужно настроить в GitHub

### 1. GitHub Secrets
Добавить в Settings → Secrets and variables → Actions:

```bash
# Обязательные:
DOMAIN=your-domain.com

# Опциональные:
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### 2. GitHub Environments
Создать в Settings → Environments:

#### Environment: `staging`
- **Protection rules**: 
  - ✅ Require a reviewer to approve new deployments
  - ✅ Restrict deployments to matching branches: `develop`
- **Environment variables**:
  - `ENVIRONMENT=staging`
  - `DOMAIN=staging.your-domain.com`

#### Environment: `production`
- **Protection rules**:
  - ✅ Require a reviewer to approve new deployments
  - ✅ Restrict deployments to matching branches: `main`
- **Environment variables**:
  - `ENVIRONMENT=production`
  - `DOMAIN=your-domain.com`

### 3. Branch Protection Rules
Настроить в Settings → Branches:

#### Для ветки `main`:
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators
- ✅ Restrict pushes that create files that use the git push --force-with-lease command

#### Для ветки `develop`:
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging

## 🔄 Workflow процессов

### Автоматический деплой:
- **Push в `develop`** → автоматический деплой в staging
- **Push в `main`** → автоматический деплой в production
- **Pull Request** → автоматическое тестирование

### Тестирование:
- Backend: pytest, black, isort, flake8
- Frontend: npm test, npm run lint
- Безопасность: safety, npm audit, Trivy

### Сборка:
- Docker образы для backend и frontend
- Публикация в GitHub Container Registry
- Тегирование по версиям

## 🚀 Команды для тестирования

### Локальное тестирование:
```bash
# Установка зависимостей
make install

# Тестирование
make test

# Линтинг
make lint

# Сборка Docker образов
make docker-build

# Запуск staging
make staging

# Запуск production
make production
```

### Деплой:
```bash
# Деплой в staging
./scripts/deploy-simple.sh staging

# Деплой в production
./scripts/deploy-simple.sh production
```

## 📊 Порты по умолчанию

- **Development**: 8000 (backend), 3000 (frontend), 5432 (DB)
- **Staging**: 8001 (backend), 3001 (frontend), 5433 (DB)
- **Production**: 8000 (backend), 3000 (frontend), 5432 (DB)

## 🔒 Безопасность

### Сканирование уязвимостей:
- **Python**: safety для проверки зависимостей
- **Node.js**: npm audit для проверки пакетов
- **Docker**: Trivy для сканирования образов
- **Автоматическое**: каждую неделю в понедельник

### Health checks:
- Backend: `GET /health`
- Frontend: `GET /`

## 📝 Следующие шаги после настройки

1. **Протестировать GitHub Actions**:
   - Перейти в GitHub → Actions
   - Убедиться, что workflows запускаются
   - Проверить, что все тесты проходят

2. **Настроить сервер для деплоя**:
   - Установить Docker и Docker Compose
   - Настроить доступ к GitHub Container Registry
   - Настроить домены и SSL сертификаты

3. **Протестировать деплой**:
   - Сделать push в ветку develop
   - Проверить деплой в staging
   - Протестировать приложение

4. **Настроить мониторинг**:
   - Настроить логирование
   - Настроить уведомления
   - Настроить метрики

## 🆘 Возможные проблемы

### Частые проблемы:
1. **Ошибка доступа к registry** - проверить права доступа
2. **Ошибка сборки образа** - проверить Dockerfile
3. **Ошибка деплоя** - проверить переменные окружения
4. **Сервис не отвечает** - проверить health checks

### Полезные команды:
```bash
# Проверка статуса
make status

# Просмотр логов
make logs

# Health checks
make monitor

# Очистка
make clean-all
```

## 🎯 Ожидаемый результат

После настройки у вас будет:
- ✅ Автоматическое тестирование при каждом push
- ✅ Автоматический деплой в staging/production
- ✅ Сканирование безопасности
- ✅ Мониторинг и логирование
- ✅ Возможность отката деплоя
- ✅ Простое управление через Makefile

---

**Готово к настройке! 🚀**
