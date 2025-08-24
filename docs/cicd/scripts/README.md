# 📜 Скрипты деплоя APEX

## 🎯 Обзор

В этой директории собраны все скрипты для автоматизации деплоя проекта APEX.

## 📁 Структура скриптов

### **Корневые скрипты**
- `scripts/deploy.sh` - Полный скрипт деплоя с Kubernetes
- `scripts/deploy-simple.sh` - Упрощенный скрипт деплоя с Docker Compose

### **GitHub Actions**
- `.github/workflows/ci-cd.yml` - Основной CI/CD пайплайн
- `.github/workflows/ci-cd-simple.yml` - Упрощенный CI/CD пайплайн
- `.github/workflows/deploy-kubernetes.yml` - Деплой в Kubernetes

## 🚀 Скрипты деплоя

### **deploy-simple.sh** - Упрощенный деплой

**Назначение:** Деплой с использованием Docker Compose (без Kubernetes)

**Использование:**
```bash
# Деплой в staging
./scripts/deploy-simple.sh staging

# Деплой в production
./scripts/deploy-simple.sh production

# Деплой конкретной версии
./scripts/deploy-simple.sh production v1.2.3
```

**Функции:**
- ✅ Проверка окружения
- ✅ Сборка Docker образов
- ✅ Деплой через Docker Compose
- ✅ Health checks
- ✅ Уведомления в Slack
- ✅ Rollback функциональность

### **deploy.sh** - Полный деплой

**Назначение:** Деплой с использованием Kubernetes

**Использование:**
```bash
# Деплой в staging
./scripts/deploy.sh staging

# Деплой в production
./scripts/deploy.sh production

# Деплой конкретной версии
./scripts/deploy.sh production v1.2.3
```

**Функции:**
- ✅ Проверка kubectl
- ✅ Применение Kubernetes манифестов
- ✅ Rolling updates
- ✅ Health checks
- ✅ Уведомления в Slack
- ✅ Rollback функциональность

## 🔧 GitHub Actions Workflows

### **ci-cd-simple.yml** - Упрощенный CI/CD

**Триггеры:**
- Push в `develop` → деплой в staging
- Push в `main` → деплой в production
- Pull Request → только тестирование

**Этапы:**
1. **Setup** - настройка окружения
2. **Test** - запуск тестов
3. **Build** - сборка Docker образов
4. **Deploy** - деплой в соответствующее окружение

### **ci-cd.yml** - Полный CI/CD

**Триггеры:**
- Push в `develop` → деплой в staging
- Push в `main` → деплой в production
- Pull Request → только тестирование

**Этапы:**
1. **Setup** - настройка окружения
2. **Test** - запуск тестов
3. **Build** - сборка Docker образов
4. **Deploy** - деплой в Kubernetes
5. **Verify** - проверка деплоя

### **deploy-kubernetes.yml** - Деплой в Kubernetes

**Назначение:** Ручной деплой в Kubernetes

**Использование:**
1. Перейдите в GitHub Actions
2. Выберите "Deploy to Kubernetes"
3. Выберите окружение и версию
4. Нажмите "Run workflow"

## 🛠️ Команды Makefile

### **Основные команды**
```bash
# Деплой
make deploy-staging
make deploy-production

# Тестирование
make test
make test-backend
make test-frontend

# Линтинг
make lint
make lint-backend
make lint-frontend

# Сборка
make docker-build
make docker-push

# Мониторинг
make status
make logs
make logs-staging
make logs-production
```

### **Безопасность**
```bash
# Сканирование безопасности
make security-scan

# Резервное копирование
make backup
make backup-staging
```

## 🔒 Безопасность

### **Переменные окружения**
- Все секреты хранятся в GitHub Secrets
- Переменные окружения в `.env` файлах
- SSL сертификаты для production

### **Проверки безопасности**
- Сканирование уязвимостей в зависимостях
- Проверка Docker образов
- Аудит кода

## 📊 Мониторинг

### **Health Checks**
- Backend: `GET /health`
- Frontend: `GET /`
- Database: PostgreSQL readiness
- Redis: Ping проверка

### **Логи**
```bash
# Логи development
make logs

# Логи staging
make logs-staging

# Логи production
make logs-production
```

## 🔄 Rollback

### **Автоматический rollback**
1. Перейдите в GitHub Actions
2. Выберите "Rollback Deployment"
3. Выберите окружение и версию
4. Нажмите "Run workflow"

### **Ручной rollback**
```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml down
TAG=v1.2.2 docker-compose -f docker-compose.prod.yml up -d

# Kubernetes
kubectl rollout undo deployment/backend -n production
kubectl rollout undo deployment/frontend -n production
```

## 🚨 Troubleshooting

### **Частые проблемы**

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

### **Полезные команды**
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

## 📈 Метрики

### **Время деплоя**
- Staging: ~3-5 минут
- Production: ~5-8 минут

### **Code Coverage**
- Backend: генерируется в `backend/htmlcov/`
- Frontend: генерируется в `frontend/coverage/`

### **Уведомления**
- Slack уведомления о статусе деплоя
- GitHub Actions статус в репозитории

## 🔮 Будущее развитие

### **Планируемые улучшения:**
1. **Blue-Green деплой** - нулевое время простоя
2. **Canary деплой** - постепенное развертывание
3. **Автоматический rollback** - при ошибках
4. **Мониторинг деплоя** - метрики и алерты
5. **Multi-region деплой** - географическое распределение
