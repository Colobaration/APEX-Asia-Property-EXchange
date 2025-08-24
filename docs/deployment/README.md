# 🚀 Развертывание APEX

## 🎯 Обзор

Эта директория содержит документацию по развертыванию системы APEX Asia Property Exchange в различных окружениях.

## 📁 Структура

```
docs/deployment/
├── README.md                    # Этот файл - обзор развертывания
└── PORTAINER_SETUP.md           # Настройка Portainer
```

## 📋 Документация по развертыванию

### **PORTAINER_SETUP.md** - Настройка Portainer
**Назначение:** Полная инструкция по настройке автоматического деплоя через Portainer

**Содержит:**
- ✅ Настройка Git Repository в Portainer
- ✅ Конфигурация переменных окружения
- ✅ Настройка GitOps для автоматического обновления
- ✅ Мониторинг сервисов
- ✅ Troubleshooting

**Для кого:** DevOps инженеры, системные администраторы

## 🚀 Варианты развертывания

### **1. Docker Compose (рекомендуется для начала)**
```bash
# Staging окружение
docker-compose -f docker-compose.staging.yml up -d

# Production окружение
docker-compose -f docker-compose.prod.yml up -d

# Локальная разработка
docker-compose -f docker-compose.local.yml up -d
```

### **2. Portainer (автоматический деплой)**
```bash
# Настройка через веб-интерфейс Portainer
# Автоматическое обновление при изменениях в Git
```

### **3. Kubernetes (production)**
```bash
# Применение манифестов
kubectl apply -f k8s/

# Проверка статуса
kubectl get pods -n apex
```

## 🔧 Конфигурация окружений

### **Staging окружение**
```yaml
# docker-compose.staging.yml
environment:
  - ENVIRONMENT=staging
  - DEBUG=false
  - LOG_LEVEL=INFO
  - DB_NAME=asia_crm_staging
```

### **Production окружение**
```yaml
# docker-compose.prod.yml
environment:
  - ENVIRONMENT=production
  - DEBUG=false
  - LOG_LEVEL=WARNING
  - DB_NAME=asia_crm_production
```

### **Локальная разработка**
```yaml
# docker-compose.local.yml
environment:
  - ENVIRONMENT=development
  - DEBUG=true
  - LOG_LEVEL=DEBUG
  - DB_NAME=asia_crm_dev
```

## 🐳 Docker Compose файлы

### **Основные файлы**
- `docker-compose.yml` - основная конфигурация
- `docker-compose.staging.yml` - staging окружение
- `docker-compose.prod.yml` - production окружение
- `docker-compose.local.yml` - локальная разработка

### **Сервисы**
```yaml
services:
  backend:      # FastAPI сервер
  frontend:     # Next.js приложение
  db:           # PostgreSQL база данных
  redis:        # Redis кэш
  nginx:        # Веб-сервер (опционально)
  metabase:     # Аналитический дашборд (опционально)
```

## 🔒 Безопасность

### **Переменные окружения**
```bash
# Обязательные секреты
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here
DB_PASSWORD=your_db_password_here
REDIS_PASSWORD=your_redis_password_here

# amoCRM интеграция
AMOCRM_CLIENT_ID=your_client_id
AMOCRM_CLIENT_SECRET=your_client_secret
AMOCRM_DOMAIN=your_domain.amocrm.ru
```

### **SSL/TLS сертификаты**
```bash
# Для production
nginx/ssl/
├── certificate.crt
├── private.key
└── dhparam.pem
```

## 📊 Мониторинг

### **Health Checks**
```bash
# Backend
curl http://your-server:8000/health

# Frontend
curl http://your-server:3000/

# Database
docker-compose exec db pg_isready -U asia

# Redis
docker-compose exec redis redis-cli ping
```

### **Логи**
```bash
# Все сервисы
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Фильтр по ошибкам
docker-compose logs backend | grep ERROR
```

### **Метрики**
```bash
# Prometheus (если настроен)
curl http://your-server:9090/metrics

# Grafana (если настроен)
open http://your-server:3001
```

## 🔄 Автоматическое развертывание

### **Portainer GitOps**
1. Настройте Git Repository в Portainer
2. Включите GitOps updates
3. Установите Fetch interval (например, 2 минуты)
4. Portainer будет автоматически обновлять stack при изменениях

### **GitHub Actions**
```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main, staging]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ./scripts/deploy.sh ${{ github.ref_name }}
```

## 🚨 Troubleshooting

### **Сервис не запускается**
```bash
# Проверить статус контейнеров
docker-compose ps

# Проверить логи
docker-compose logs service_name

# Проверить переменные окружения
docker-compose exec service_name env
```

### **Проблемы с базой данных**
```bash
# Проверить подключение
docker-compose exec db pg_isready -U asia

# Проверить логи БД
docker-compose logs db

# Восстановить из backup
docker-compose exec db psql -U asia -d asia_crm -f backup.sql
```

### **Проблемы с сетью**
```bash
# Проверить порты
netstat -tulpn | grep :8000

# Проверить DNS
nslookup your-domain.com

# Проверить firewall
sudo ufw status
```

## 📈 Масштабирование

### **Горизонтальное масштабирование**
```bash
# Увеличить количество backend контейнеров
docker-compose up -d --scale backend=3

# Load balancer (если настроен)
docker-compose up -d nginx
```

### **Вертикальное масштабирование**
```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
```

## 🔄 Backup и восстановление

### **Backup базы данных**
```bash
# Создать backup
docker-compose exec db pg_dump -U asia asia_crm > backup.sql

# Автоматический backup
./scripts/backup.sh
```

### **Восстановление**
```bash
# Восстановить из backup
docker-compose exec db psql -U asia -d asia_crm < backup.sql

# Восстановить конкретную таблицу
docker-compose exec db psql -U asia -d asia_crm -c "COPY table_name FROM '/backup/table.csv' CSV;"
```

## 🔗 Связанная документация

- [CI/CD документация](../cicd/README.md) - автоматизация деплоя
- [Настройка](../setup/README.md) - настройка компонентов
- [Архитектура](../ARCHITECTURE.md) - архитектура системы
- [Быстрый старт](../quickstart/README.md) - быстрый старт

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи сервисов
2. Убедитесь, что все переменные окружения корректны
3. Проверьте доступность портов и сервисов
4. Обратитесь к документации в соответствующих разделах
5. Создайте issue в репозитории

---

**Развертывание системы APEX завершено! 🎉**
