# Краткий обзор корня проекта APEX

## 🎯 Основные компоненты

### **📦 Приложения**
- `backend/` - FastAPI сервер (Python)
- `frontend/` - Next.js приложение (TypeScript)

### **🔧 Конфигурация**
- `docker-compose.yml` - Основной Docker Compose
- `Makefile` - Команды управления проектом
- `env.example` - Шаблон переменных окружения
- `.pre-commit-config.yaml` - Pre-commit хуки

### **📚 Документация**
- `docs/` - Основная документация
- `README.md` - Главная документация
- `QUICKSTART.md` - Быстрый старт

### **🚀 DevOps**
- `.github/workflows/` - GitHub Actions
- `k8s/` - Kubernetes манифесты
- `nginx/` - Nginx конфигурации
- `scripts/` - Утилитарные скрипты

## 🔄 Workflow

### **Разработка**
```bash
# Установка
make install

# Запуск
make dev

# Тестирование
make test
```

### **Развертывание**
```bash
# Docker
make docker-up

# Kubernetes
./scripts/deploy.sh production
```

## 🛡️ Безопасность

### **Pre-commit хуки**
- **Python**: Black, isort, Ruff, MyPy, Bandit
- **Frontend**: ESLint, Prettier
- **Общие**: YAML/JSON проверки, trailing whitespace

### **Переменные окружения**
- `env.example` - шаблон
- `.env` - локальные настройки (не в Git)
- `portainer-staging.env` - staging настройки

## 📊 Мониторинг

### **Health Checks**
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000`
- Database: PostgreSQL readiness
- Redis: Ping проверка

### **Логирование**
- Структурированные логи
- Разные уровни (DEBUG, INFO, WARNING, ERROR)
- Ротация логов

## 🎯 Ключевые особенности

### **1. Модульность**
- Разделение backend/frontend
- Независимые конфигурации
- Модульная документация

### **2. Многоокружение**
- Development (локальная разработка)
- Staging (тестовое окружение)
- Production (продакшн)

### **3. Автоматизация**
- Makefile команды
- GitHub Actions CI/CD
- Docker Compose
- Скрипты развертывания

### **4. Безопасность**
- Переменные окружения
- Secrets management
- Code owners
- Security scanning

### **5. Качество кода**
- Pre-commit хуки
- Линтеры и форматтеры
- Type checking
- Security scanning

## 📈 Масштабирование

### **Горизонтальное**
- Kubernetes кластер
- Load balancer
- Репликация БД

### **Вертикальное**
- Увеличение ресурсов
- Оптимизация кода
- Кэширование

## 🔮 Будущее развитие

### **Планируемые улучшения:**
1. **Микросервисы** - разделение на сервисы
2. **Event-driven** - асинхронная архитектура
3. **Monitoring** - Prometheus + Grafana
4. **Security** - OAuth2 + 2FA
5. **Performance** - CDN + кэширование
6. **Mobile** - React Native приложение
