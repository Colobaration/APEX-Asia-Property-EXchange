# 🚀 CI/CD Pipeline для APEX Asia Property Exchange

Полная система автоматического деплоя с использованием GitHub Actions и Kubernetes.

## 📋 Быстрый старт

### 1. Настройка GitHub Secrets

Добавьте следующие секреты в настройках репозитория (`Settings` → `Secrets and variables` → `Actions`):

```bash
# Kubernetes конфигурация (base64 encoded)
KUBE_CONFIG=<base64-encoded-kubeconfig>

# Slack уведомления
SLACK_WEBHOOK=<slack-webhook-url>

# Домены
DOMAIN=<your-domain.com>
```

### 2. Создание Environments

Создайте environments в настройках репозитория:
- `staging` - для тестового окружения
- `production` - для продакшена

### 3. Настройка Kubernetes кластера

Убедитесь, что у вас настроен Kubernetes кластер с:
- Ingress контроллером (nginx-ingress)
- cert-manager для SSL сертификатов
- Доступом к GitHub Container Registry

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
./scripts/deploy.sh staging

# Деплой в production
./scripts/deploy.sh production

# Деплой конкретной версии
./scripts/deploy.sh production v1.2.3
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

# Kubernetes команды
make k8s-apply
make k8s-status
make k8s-logs

# Безопасность
make security-scan

# Мониторинг
make monitor
```

## 📁 Структура файлов

```
.github/
├── workflows/
│   ├── ci-cd.yml              # Основной CI/CD pipeline
│   ├── security-scan.yml      # Сканирование безопасности
│   ├── deploy-kubernetes.yml  # Деплой в Kubernetes
│   └── rollback.yml          # Откат деплоя
└── variables.env             # Переменные окружения

k8s/
├── namespace.yaml            # Namespaces
├── configmap.yaml           # Конфигурация
├── secrets.yaml             # Секреты
├── backend-deployment.yaml  # Backend deployment
├── frontend-deployment.yaml # Frontend deployment
├── backend-service.yaml     # Backend service
├── frontend-service.yaml    # Frontend service
└── ingress.yaml            # Ingress

scripts/
└── deploy.sh               # Скрипт деплоя

docs/
└── ci-cd-setup.md         # Подробная документация
```

## 🔒 Безопасность

### Сканирование уязвимостей

- **Python**: `safety` для проверки зависимостей
- **Node.js**: `npm audit` для проверки пакетов
- **Docker**: `Trivy` для сканирования образов
- **Автоматическое**: каждую неделю в понедельник

### Секреты

- Все чувствительные данные в Kubernetes Secrets
- Переменные окружения в ConfigMaps
- GitHub Secrets для CI/CD

## 📊 Мониторинг

### Health Checks

- Backend: `GET /health`
- Frontend: `GET /`

### Логи

```bash
# Логи backend
kubectl logs -f deployment/backend -n staging

# Логи frontend
kubectl logs -f deployment/frontend -n staging

# События кластера
kubectl get events -n staging --sort-by='.lastTimestamp'
```

### Статус сервисов

```bash
# Статус подов
kubectl get pods -n staging

# Статус сервисов
kubectl get services -n staging

# Статус ingress
kubectl get ingress -n staging
```

## 🔄 Откат деплоя

### Автоматический откат

1. Перейдите в GitHub Actions
2. Выберите "Rollback Deployment"
3. Выберите окружение и версию
4. Нажмите "Run workflow"

### Ручной откат

```bash
# Откат к предыдущей версии
kubectl rollout undo deployment/backend -n production
kubectl rollout undo deployment/frontend -n production

# Откат к конкретной версии
kubectl set image deployment/backend backend=ghcr.io/your-repo/backend:v1.2.2 -n production
kubectl set image deployment/frontend frontend=ghcr.io/your-repo/frontend:v1.2.2 -n production
```

## 🚨 Troubleshooting

### Частые проблемы

1. **Ошибка сборки образа**
   ```bash
   # Проверьте Dockerfile
   docker build -t test ./backend
   
   # Проверьте зависимости
   make install
   ```

2. **Ошибка деплоя в Kubernetes**
   ```bash
   # Проверьте права доступа
   kubectl auth can-i create deployments --namespace staging
   
   # Проверьте манифесты
   kubectl apply -f k8s/ --dry-run=client
   ```

3. **Сервис не отвечает**
   ```bash
   # Проверьте health checks
   kubectl describe pod <pod-name> -n staging
   
   # Проверьте логи
   kubectl logs <pod-name> -n staging
   
   # Проверьте ingress
   kubectl describe ingress app-ingress -n staging
   ```

### Полезные команды

```bash
# Описание пода
kubectl describe pod <pod-name> -n <namespace>

# Подключение к поду
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Просмотр конфигурации
kubectl get configmap app-config -n <namespace> -o yaml
kubectl get secret app-secrets -n <namespace> -o yaml

# Перезапуск деплоймента
kubectl rollout restart deployment/backend -n <namespace>
```

## 📈 Метрики и аналитика

### Code Coverage

- Backend: генерируется в `backend/htmlcov/`
- Frontend: генерируется в `frontend/coverage/`
- Отправляется в Codecov

### Время деплоя

- Staging: ~5-10 минут
- Production: ~10-15 минут

### Уведомления

- Slack уведомления о статусе деплоя
- Email уведомления о критических ошибках
- GitHub Actions статус в репозитории

## 🔧 Настройка для новых проектов

1. Скопируйте файлы CI/CD в ваш проект
2. Обновите переменные в `.github/variables.env`
3. Настройте GitHub Secrets
4. Создайте Kubernetes кластер
5. Обновите домены в манифестах
6. Протестируйте pipeline

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи GitHub Actions
2. Проверьте статус Kubernetes ресурсов
3. Обратитесь к документации в `docs/ci-cd-setup.md`
4. Создайте issue в репозитории

---

**Удачного деплоя! 🚀**
