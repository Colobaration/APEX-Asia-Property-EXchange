# Настройка CI/CD для APEX Asia Property Exchange

## Обзор

Этот проект использует GitHub Actions для автоматического тестирования, сборки и деплоя приложения в Kubernetes кластер.

## Архитектура CI/CD

### Workflows

1. **CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)
   - Тестирование backend и frontend
   - Сборка Docker образов
   - Публикация в GitHub Container Registry
   - Деплой в staging/production

2. **Security Scan** (`.github/workflows/security-scan.yml`)
   - Сканирование уязвимостей в зависимостях
   - Проверка Docker образов
   - Еженедельное автоматическое сканирование

3. **Kubernetes Deploy** (`.github/workflows/deploy-kubernetes.yml`)
   - Деплой в Kubernetes кластер
   - Проверка здоровья сервисов
   - Уведомления в Slack

4. **Rollback** (`.github/workflows/rollback.yml`)
   - Откат деплоя в случае проблем
   - Ручной запуск через GitHub Actions

## Настройка окружения

### 1. GitHub Secrets

Добавьте следующие секреты в настройках репозитория:

```bash
# Kubernetes
KUBE_CONFIG=<base64-encoded-kubeconfig>

# Slack уведомления
SLACK_WEBHOOK=<slack-webhook-url>

# Домены
DOMAIN=<your-domain.com>
```

### 2. GitHub Environments

Создайте environments в настройках репозитория:
- `staging` - для тестового окружения
- `production` - для продакшена

### 3. Kubernetes кластер

Убедитесь, что у вас настроен Kubernetes кластер с:
- Ingress контроллером (nginx-ingress)
- cert-manager для SSL сертификатов
- Доступом к GitHub Container Registry

## Структура Kubernetes манифестов

```
k8s/
├── namespace.yaml          # Namespaces для staging/production
├── configmap.yaml          # Конфигурация приложения
├── secrets.yaml            # Секретные данные
├── backend-deployment.yaml # Backend deployment
├── frontend-deployment.yaml # Frontend deployment
├── backend-service.yaml    # Backend service
├── frontend-service.yaml   # Frontend service
└── ingress.yaml           # Ingress для маршрутизации
```

## Процесс деплоя

### Автоматический деплой

1. **Push в develop ветку** → Деплой в staging
2. **Push в main ветку** → Деплой в production
3. **Pull Request** → Только тестирование

### Ручной деплой

```bash
# Деплой в staging
./scripts/deploy.sh staging

# Деплой в production
./scripts/deploy.sh production

# Деплой конкретной версии
./scripts/deploy.sh production v1.2.3
```

### Откат деплоя

1. Через GitHub Actions → Actions → Rollback Deployment
2. Или через kubectl:
```bash
kubectl rollout undo deployment/backend -n production
kubectl rollout undo deployment/frontend -n production
```

## Мониторинг и логи

### Проверка статуса деплоя

```bash
# Статус подов
kubectl get pods -n staging
kubectl get pods -n production

# Логи приложений
kubectl logs -f deployment/backend -n staging
kubectl logs -f deployment/frontend -n staging

# Статус сервисов
kubectl get services -n staging
kubectl get endpoints -n staging
```

### Health checks

- Backend: `GET /health`
- Frontend: `GET /`

## Безопасность

### Сканирование уязвимостей

- **Python**: safety для проверки зависимостей
- **Node.js**: npm audit для проверки пакетов
- **Docker**: Trivy для сканирования образов

### Секреты

- Все чувствительные данные хранятся в Kubernetes Secrets
- Переменные окружения в ConfigMaps
- GitHub Secrets для CI/CD

## Troubleshooting

### Частые проблемы

1. **Ошибка сборки образа**
   - Проверьте Dockerfile
   - Убедитесь в корректности зависимостей

2. **Ошибка деплоя в Kubernetes**
   - Проверьте права доступа к кластеру
   - Убедитесь в корректности манифестов

3. **Сервис не отвечает**
   - Проверьте health checks
   - Проверьте логи подов
   - Проверьте настройки Ingress

### Полезные команды

```bash
# Описание пода
kubectl describe pod <pod-name> -n <namespace>

# Подключение к поду
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Просмотр событий
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Проверка конфигурации
kubectl get configmap app-config -n <namespace> -o yaml
kubectl get secret app-secrets -n <namespace> -o yaml
```

## Обновление конфигурации

### Изменение переменных окружения

1. Обновите `k8s/configmap.yaml` или `k8s/secrets.yaml`
2. Примените изменения:
```bash
kubectl apply -f k8s/configmap.yaml -n <namespace>
kubectl apply -f k8s/secrets.yaml -n <namespace>
```
3. Перезапустите деплойменты:
```bash
kubectl rollout restart deployment/backend -n <namespace>
kubectl rollout restart deployment/frontend -n <namespace>
```

### Обновление версии приложения

1. Создайте новый тег:
```bash
git tag v1.2.3
git push origin v1.2.3
```

2. Или используйте commit hash:
```bash
./scripts/deploy.sh production $(git rev-parse --short HEAD)
```
