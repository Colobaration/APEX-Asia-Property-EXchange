# 📚 Документация APEX

## 🎯 Обзор

Добро пожаловать в документацию системы APEX Asia Property Exchange! Эта директория содержит всю необходимую документацию для разработки, развертывания и сопровождения системы.

## 📁 Структура документации

```
docs/
├── README.md                    # Этот файл - главная документация
├── SECURITY.md                  # Безопасность системы
├── CHANGELOG.md                 # История изменений
├── FINAL-REPORT.md              # Финальный отчет
├── ROOT_OVERVIEW.md             # Обзор корня проекта
├── PROJECT_ROOT_STRUCTURE.md    # Структура корня проекта
├── CICD_REORGANIZATION.md       # Реорганизация CI/CD
├── quickstart/                  # Быстрый старт
│   └── README.md
├── setup/                       # Настройка компонентов
│   ├── README.md
│   ├── MIGRATION_SYSTEM_SUMMARY.md
│   ├── API_SERVER_README.md
│   └── WEBHOOK_SETUP.md
├── deployment/                  # Развертывание
│   ├── README.md
│   └── PORTAINER_SETUP.md
├── cicd/                        # CI/CD документация
│   ├── README.md
│   ├── ci-cd-setup.md
│   ├── simple/                  # Простая версия CI/CD
│   ├── kubernetes/              # Kubernetes версия CI/CD
│   ├── guides/                  # Руководства
│   └── scripts/                 # Документация скриптов
├── integrations/                # Внешние интеграции
│   ├── README.md
│   ├── amocrm-integration-guide.md
│   ├── amocrm-setup.md
│   ├── webhook-quickstart.md
│   └── webhook-server-setup.md
├── testing/                     # Тестирование
│   ├── README.md
│   └── test-plan.md
├── architecture/                # Архитектура
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── DESIGN_LOG.md
│   └── REFACTOR_PLAN.md
└── project/                     # Проект
    ├── README.md
    ├── project-structure.md
    ├── endpoints.md
    ├── crm-fields.md
    └── pipelines.md
```

## 🚀 Быстрый навигатор

### **Для новых разработчиков**
1. **[Быстрый старт](./quickstart/README.md)** - начните здесь
2. **[Архитектура](./architecture/README.md)** - понимание системы
3. **[Настройка](./setup/README.md)** - настройка компонентов

### **Для DevOps инженеров**
1. **[Развертывание](./deployment/README.md)** - развертывание системы
2. **[CI/CD документация](./cicd/README.md)** - автоматизация
3. **[Безопасность](./SECURITY.md)** - безопасность системы

### **Для разработчиков**
1. **[Проект](./project/README.md)** - структура проекта
2. **[Интеграции](./integrations/README.md)** - внешние интеграции
3. **[Тестирование](./testing/README.md)** - тестирование

### **Для архитекторов**
1. **[Архитектура](./architecture/README.md)** - детальная архитектура
2. **[Design Log](./architecture/DESIGN_LOG.md)** - история решений
3. **[Refactor Plan](./architecture/REFACTOR_PLAN.md)** - планы развития

## 📋 Основные разделы

### **🏗️ Архитектура**
- [Обзор архитектуры](./architecture/README.md)
- [Детальная архитектура](./architecture/ARCHITECTURE.md)
- [Лог проектирования](./architecture/DESIGN_LOG.md)
- [План рефакторинга](./architecture/REFACTOR_PLAN.md)

### **🚀 Развертывание**
- [Обзор развертывания](./deployment/README.md)
- [Настройка Portainer](./deployment/PORTAINER_SETUP.md)
- [Docker Compose файлы](../docker-compose.yml)

### **🔧 Настройка**
- [Обзор настройки](./setup/README.md)
- [Система миграций](./setup/MIGRATION_SYSTEM_SUMMARY.md)
- [API сервер](./setup/API_SERVER_README.md)
- [Webhook настройка](./setup/WEBHOOK_SETUP.md)

### **🔄 CI/CD**
- [Обзор CI/CD](./cicd/README.md)
- [Простая версия](./cicd/simple/README-CI-CD-SIMPLE.md)
- [Kubernetes версия](./cicd/kubernetes/README-CI-CD.md)
- [Руководства](./cicd/guides/)

### **🔗 Интеграции**
- [Обзор интеграций](./integrations/README.md)
- [AmoCRM интеграция](./integrations/amocrm-integration-guide.md)
- [Настройка AmoCRM](./integrations/amocrm-setup.md)
- [Webhook настройка](./integrations/webhook-quickstart.md)

### **🧪 Тестирование**
- [Обзор тестирования](./testing/README.md)
- [План тестирования](./testing/test-plan.md)

### **📋 Проект**
- [Обзор проекта](./project/README.md)
- [Структура проекта](./project/project-structure.md)
- [API endpoints](./project/endpoints.md)
- [CRM поля](./project/crm-fields.md)
- [Воронка продаж](./project/pipelines.md)

## 🎯 Ключевые документы

### **Безопасность**
- [SECURITY.md](./SECURITY.md) - полная документация по безопасности

### **История изменений**
- [CHANGELOG.md](./CHANGELOG.md) - история изменений проекта

### **Финальный отчет**
- [FINAL-REPORT.md](./FINAL-REPORT.md) - итоговый отчет по проекту

### **Структура проекта**
- [ROOT_OVERVIEW.md](./ROOT_OVERVIEW.md) - обзор корня проекта
- [PROJECT_ROOT_STRUCTURE.md](./PROJECT_ROOT_STRUCTURE.md) - детальная структура

## 🔍 Поиск документации

### **По теме**
- **Безопасность**: [SECURITY.md](./SECURITY.md)
- **API**: [endpoints.md](./project/endpoints.md)
- **База данных**: [MIGRATION_SYSTEM_SUMMARY.md](./setup/MIGRATION_SYSTEM_SUMMARY.md)
- **Docker**: [deployment/README.md](./deployment/README.md)
- **Kubernetes**: [cicd/kubernetes/README-CI-CD.md](./cicd/kubernetes/README-CI-CD.md)

### **По роли**
- **Разработчик**: [project/README.md](./project/README.md)
- **DevOps**: [deployment/README.md](./deployment/README.md)
- **QA**: [testing/README.md](./testing/README.md)
- **Архитектор**: [architecture/README.md](./architecture/README.md)

## 🚀 Быстрый старт

### **1. Установка и настройка**
```bash
# Клонирование репозитория
git clone <repository>
cd APEX-Asia-Property-EXchange

# Установка зависимостей
make install

# Настройка переменных окружения
cp env.example .env
# Отредактируйте .env файл

# Запуск в режиме разработки
make dev
```

### **2. Доступ к сервисам**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Metabase**: http://localhost:3001

### **3. Первые шаги**
1. Изучите [архитектуру](./architecture/README.md)
2. Настройте [интеграции](./integrations/README.md)
3. Запустите [тесты](./testing/README.md)
4. Настройте [CI/CD](./cicd/README.md)

## 🔧 Полезные команды

### **Разработка**
```bash
# Запуск всех сервисов
make dev

# Только backend
cd backend && make dev

# Только frontend
cd frontend && make dev
```

### **Тестирование**
```bash
# Все тесты
make test

# Backend тесты
make test-backend

# Frontend тесты
make test-frontend
```

### **Развертывание**
```bash
# Docker Compose
make docker-up

# Kubernetes
./scripts/deploy.sh staging
```

## 📞 Поддержка

### **При возникновении проблем**
1. Проверьте [troubleshooting](./setup/README.md#🚨-troubleshooting)
2. Изучите [логи](./deployment/README.md#📊-мониторинг)
3. Обратитесь к соответствующей документации
4. Создайте issue в репозитории

### **Полезные ссылки**
- [GitHub Issues](https://github.com/your-repo/issues)
- [API Documentation](http://localhost:8000/docs)
- [Metabase Dashboard](http://localhost:3001)

## 🔮 Развитие документации

### **Планы по улучшению**
1. **Интерактивные диаграммы** - Mermaid диаграммы
2. **Видео туториалы** - скринкасты
3. **Поиск по документации** - полнотекстовый поиск
4. **Версионирование** - версии документации

### **Вклад в документацию**
1. Создайте feature branch
2. Внесите изменения
3. Обновите соответствующие README файлы
4. Создайте Pull Request

---

**Документация APEX готова к использованию! 🎉**

Начните с [быстрого старта](./quickstart/README.md) или выберите интересующий вас раздел из навигатора выше.
