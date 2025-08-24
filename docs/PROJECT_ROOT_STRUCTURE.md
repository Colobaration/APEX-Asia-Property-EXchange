# Структура корня проекта APEX

## 🏗️ Обзор

Корень проекта APEX содержит все необходимые файлы для разработки, развертывания и управления проектом. Структура организована по принципу разделения ответственности и удобства разработки.

## 📁 Детальная структура

```
APEX-Asia-Property-EXchange-/
├── 📦 Основные компоненты
│   ├── backend/                    # FastAPI Backend
│   └── frontend/                   # Next.js Frontend
│
├── 🔧 Конфигурация и развертывание
│   ├── docker-compose.yml          # Основной Docker Compose
│   ├── docker-compose.local.yml    # Локальная разработка
│   ├── docker-compose.staging.yml  # Staging окружение
│   ├── docker-compose.prod.yml     # Production окружение
│   ├── Makefile                    # Команды управления проектом
│   ├── env.example                 # Пример переменных окружения
│   ├── .gitignore                  # Исключения Git
│   ├── .editorconfig               # Настройки редактора
│   └── .pre-commit-config.yaml     # Pre-commit хуки
│
├── 📚 Документация
│   ├── docs/                       # Основная документация
│   ├── README.md                   # Главный README
│   ├── QUICKSTART.md               # Быстрый старт
│   ├── QUICK_SETUP_GUIDE.md        # Руководство по настройке
│   ├── API_SERVER_README.md        # Документация API
│   ├── WEBHOOK_SETUP.md            # Настройка webhook'ов
│   ├── PORTAINER_SETUP.md          # Настройка Portainer
│   └── MIGRATION_SYSTEM_SUMMARY.md # Система миграций
│
├── 🚀 CI/CD и DevOps
│   ├── .github/                    # GitHub Actions
│   │   ├── workflows/              # CI/CD пайплайны
│   │   └── variables.env           # Переменные окружения
│   ├── k8s/                        # Kubernetes манифесты
│   ├── nginx/                      # Nginx конфигурации
│   ├── ops/                        # Операционные скрипты
│   └── scripts/                    # Утилитарные скрипты
│
├── 📊 Аналитика и мониторинг
│   ├── analytics/                  # Аналитические дашборды
│   └── portainer-staging.env       # Переменные Portainer
│
├── 🔒 Безопасность и управление
│   ├── CODEOWNERS                  # Владельцы кода
│   └── prompts/                    # Промпты для AI
│
└── 📋 Документация CI/CD
    ├── README-CI-CD.md             # Основная CI/CD документация
    ├── README-CI-CD-SIMPLE.md      # Упрощенная CI/CD
    ├── TEST_CI_CD.md               # Тестирование CI/CD
    ├── GITHUB_SETUP_PROMPT.md      # Настройка GitHub
    ├── CREATE_PR_INSTRUCTIONS.md   # Инструкции по PR
    └── PR_DESCRIPTION.md           # Шаблоны PR
```

## 🔧 Конфигурационные файлы

### **Docker Compose файлы**

#### 1. **docker-compose.yml** - Основной файл
```yaml
services:
  backend:      # FastAPI сервер
  frontend:     # Next.js приложение
  db:           # PostgreSQL база данных
  redis:        # Redis кэш
  metabase:     # Аналитический дашборд
```

**Назначение:**
- Основная конфигурация для разработки
- Все сервисы с health checks
- Volume mounts для hot reload
- Сетевая изоляция

#### 2. **docker-compose.local.yml** - Локальная разработка
```yaml
# Упрощенная версия для локальной разработки
# Без production сервисов
```

#### 3. **docker-compose.staging.yml** - Staging окружение
```yaml
# Конфигурация для staging сервера
# С production-like настройками
```

#### 4. **docker-compose.prod.yml** - Production окружение
```yaml
# Production конфигурация
# С оптимизациями и безопасностью
```

### **Makefile** - Управление проектом
```makefile
# Основные команды:
make help          # Справка по командам
make install       # Установка зависимостей
make dev           # Запуск в режиме разработки
make lint          # Проверка кода
make test          # Запуск тестов
make build         # Сборка проекта
make docker-up     # Запуск Docker сервисов
```

**Ключевые функции:**
- Управление всеми сервисами
- Автоматизация разработки
- CI/CD интеграция
- Удобные команды

### **env.example** - Переменные окружения
```bash
# Backend Configuration
AMOCRM_CLIENT_ID=your_amocrm_client_id
AMOCRM_CLIENT_SECRET=your_amocrm_client_secret

# Database Configuration
DB_URL=postgresql://asia:asia@db:5432/asia_crm

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here
```

**Назначение:**
- Шаблон для .env файла
- Документация переменных
- Безопасность (без реальных значений)

## 📚 Документация

### **docs/** - Основная документация
- `ARCHITECTURE.md` - Архитектура системы
- `SECURITY.md` - Безопасность
- `DESIGN_LOG.md` - Лог проектирования
- `FINAL-REPORT.md` - Финальный отчет
- `CHANGELOG.md` - История изменений
- `REFACTOR_PLAN.md` - План рефакторинга

### **README файлы**
- `README.md` - Главная документация
- `QUICKSTART.md` - Быстрый старт
- `QUICK_SETUP_GUIDE.md` - Руководство по настройке
- `API_SERVER_README.md` - Документация API

## 🚀 CI/CD и DevOps

### **.github/workflows/** - GitHub Actions
```yaml
# Основные пайплайны:
ci.yml                    # Continuous Integration
ci-cd.yml                 # CI/CD пайплайн
ci-cd-simple.yml          # Упрощенный CI/CD
deploy-kubernetes.yml     # Развертывание в K8s
security-scan.yml         # Сканирование безопасности
rollback.yml              # Откат изменений
```

### **k8s/** - Kubernetes манифесты
```yaml
# Файлы:
namespace.yaml            # Namespace
backend-deployment.yaml   # Backend deployment
frontend-deployment.yaml  # Frontend deployment
backend-service.yaml      # Backend service
frontend-service.yaml     # Frontend service
ingress.yaml              # Ingress rules
configmap.yaml            # ConfigMap
secrets.yaml              # Secrets
```

### **nginx/** - Nginx конфигурации
```nginx
# Файлы:
nginx.conf                # Основная конфигурация
nginx-staging.conf        # Staging конфигурация
ssl/                      # SSL сертификаты
```

### **ops/** - Операционные скрипты
```bash
# Файлы:
project_bootstrap.sh      # Инициализация проекта
protect_branches.sh       # Защита веток
import_tasks.py           # Импорт задач
tasks.yaml                # Конфигурация задач
```

### **scripts/** - Утилитарные скрипты
```bash
# Файлы:
start-api.sh              # Запуск API сервера
start-webhook.sh          # Запуск webhook сервера
deploy.sh                 # Развертывание
deploy-simple.sh          # Упрощенное развертывание
test_api.sh               # Тестирование API
test_integration.py       # Интеграционные тесты
test_webhook_server.py    # Тестирование webhook
test_amocrm_integration.py # Тестирование AmoCRM
```

## 📊 Аналитика и мониторинг

### **analytics/** - Аналитические дашборды
```
analytics/
├── dashboards/           # Metabase дашборды
└── pipeline/             # ETL пайплайны
```

### **portainer-staging.env** - Переменные Portainer
```bash
# Конфигурация для Portainer
# Управление контейнерами
```

## 🔒 Безопасность и управление

### **CODEOWNERS** - Владельцы кода
```gitignore
# Определяет владельцев для разных частей кода
# Автоматические ревью
```

### **prompts/** - Промпты для AI
```
prompts/
└── README.md             # Документация промптов
```

## 📋 Документация CI/CD

### **README-CI-CD.md** - Основная CI/CD документация
- Полное описание пайплайнов
- Настройка окружений
- Troubleshooting

### **README-CI-CD-SIMPLE.md** - Упрощенная CI/CD
- Быстрая настройка
- Основные команды
- Примеры использования

### **TEST_CI_CD.md** - Тестирование CI/CD
- Тестирование пайплайнов
- Отладка проблем
- Best practices

### **GITHUB_SETUP_PROMPT.md** - Настройка GitHub
- Настройка репозитория
- Branch protection
- GitHub Actions

### **CREATE_PR_INSTRUCTIONS.md** - Инструкции по PR
- Создание Pull Request
- Code review
- Merge стратегии

### **PR_DESCRIPTION.md** - Шаблоны PR
- Шаблоны описания PR
- Чеклисты
- Форматы коммитов

## 🎯 Ключевые особенности

### **1. Модульность**
- Разделение на backend/frontend
- Независимые конфигурации
- Модульная документация

### **2. Многоокружение**
- Development
- Staging
- Production
- Локальная разработка

### **3. Автоматизация**
- Makefile команды
- GitHub Actions
- Docker Compose
- Скрипты развертывания

### **4. Безопасность**
- Переменные окружения
- Secrets management
- Code owners
- Security scanning

### **5. Мониторинг**
- Health checks
- Логирование
- Метрики
- Аналитика

## 🔄 Workflow разработки

### **1. Локальная разработка**
```bash
# Клонирование и настройка
git clone <repo>
cp env.example .env
make install
make dev
```

### **2. Тестирование**
```bash
# Запуск тестов
make test
make lint
make test-coverage
```

### **3. Развертывание**
```bash
# Staging
make docker-up
# или
./scripts/deploy.sh staging

# Production
./scripts/deploy.sh production
```

### **4. CI/CD**
```bash
# Автоматическое развертывание через GitHub Actions
# При push в main/staging ветки
```

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
