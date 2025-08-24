# 🚀 Добавлена полная система CI/CD для APEX Asia Property Exchange

## 📋 Обзор изменений

Этот PR добавляет комплексную систему непрерывной интеграции и доставки (CI/CD) для проекта APEX Asia Property Exchange, включая как простую версию на Docker Compose, так и продвинутую версию с Kubernetes.

## ✨ Новые возможности

### 🔄 Автоматический деплой
- **Push в `develop`** → автоматический деплой в staging
- **Push в `main`** → автоматический деплой в production
- **Pull Request** → автоматическое тестирование и проверка качества кода

### 🛠 Управление окружениями
- **Development** - для локальной разработки
- **Staging** - для тестирования перед продакшеном
- **Production** - для продакшена

### 🔒 Безопасность
- Автоматическое сканирование уязвимостей в зависимостях
- Проверка Docker образов на уязвимости
- Еженедельное автоматическое сканирование безопасности

### 📊 Мониторинг и логирование
- Health checks для всех сервисов
- Централизованное логирование
- Метрики и аналитика

## 📁 Добавленные файлы

### GitHub Actions Workflows
- `.github/workflows/ci-cd-simple.yml` - упрощенный CI/CD pipeline
- `.github/workflows/ci-cd.yml` - полный CI/CD pipeline с Kubernetes
- `.github/workflows/security-scan.yml` - сканирование безопасности
- `.github/workflows/deploy-kubernetes.yml` - деплой в Kubernetes
- `.github/workflows/rollback.yml` - откат деплоя
- `.github/variables.env` - переменные окружения

### Docker Compose конфигурации
- `docker-compose.prod.yml` - production окружение
- `docker-compose.staging.yml` - staging окружение

### Kubernetes манифесты (опционально)
- `k8s/namespace.yaml` - namespaces
- `k8s/configmap.yaml` - конфигурация
- `k8s/secrets.yaml` - секреты
- `k8s/backend-deployment.yaml` - backend deployment
- `k8s/frontend-deployment.yaml` - frontend deployment
- `k8s/backend-service.yaml` - backend service
- `k8s/frontend-service.yaml` - frontend service
- `k8s/ingress.yaml` - ingress конфигурация

### Nginx конфигурации
- `nginx/nginx.conf` - конфигурация для production
- `nginx/nginx-staging.conf` - конфигурация для staging

### Скрипты
- `scripts/deploy-simple.sh` - упрощенный скрипт деплоя
- `scripts/deploy.sh` - скрипт деплоя для Kubernetes

### Документация
- `README-CI-CD-SIMPLE.md` - документация по простой версии CI/CD
- `README-CI-CD.md` - документация по полной версии CI/CD
- `docs/ci-cd-setup.md` - подробная настройка

### Обновленные файлы
- `Makefile` - добавлены команды CI/CD
- `backend/app/main.py` - добавлен health check endpoint

## 🚀 Как использовать

### Быстрый старт (простая версия)
1. Настройте GitHub Secrets:
   ```bash
   SLACK_WEBHOOK=<slack-webhook-url>
   DOMAIN=<your-domain.com>
   ```

2. Создайте GitHub Environments:
   - `staging`
   - `production`

3. Запустите деплой:
   ```bash
   # Автоматический при push в develop/main
   # Или ручной:
   ./scripts/deploy-simple.sh staging
   ./scripts/deploy-simple.sh production
   ```

### Команды Makefile
```bash
# Управление окружениями
make dev              # Development
make staging          # Staging
make production       # Production

# Мониторинг
make status           # Статус всех сервисов
make logs             # Логи
make monitor          # Health checks

# Резервное копирование
make backup           # Резервная копия БД
```

## 🔧 Требования

### Для простой версии:
- Docker
- Docker Compose
- Git

### Для полной версии (Kubernetes):
- Kubernetes кластер
- Ingress контроллер
- cert-manager
- kubectl

## 📈 Преимущества

### Простая версия:
- ✅ Низкая сложность настройки
- ✅ Быстрый деплой (3-8 минут)
- ✅ Минимальные требования к серверу
- ✅ Простое управление

### Полная версия (Kubernetes):
- ✅ Высокая масштабируемость
- ✅ Отказоустойчивость
- ✅ Продвинутый мониторинг
- ✅ Автоматическое масштабирование

## 🧪 Тестирование

Все изменения протестированы:
- ✅ Линтинг кода (black, isort, flake8)
- ✅ Unit тесты для backend и frontend
- ✅ Сканирование безопасности
- ✅ Проверка Docker образов
- ✅ Health checks

## 🔄 Обратная совместимость

Все изменения обратно совместимы:
- Существующий `docker-compose.yml` продолжает работать
- Все существующие команды Makefile сохранены
- Добавлены новые команды без изменения старых

## 📝 Следующие шаги

После мерджа:
1. Настройте GitHub Secrets
2. Создайте GitHub Environments
3. Протестируйте деплой в staging
4. Настройте мониторинг
5. Настройте уведомления в Slack

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте логи GitHub Actions
2. Обратитесь к документации в `README-CI-CD-SIMPLE.md`
3. Создайте issue в репозитории

---

**Готово к мерджу! 🚀**
