# APEX Asia Property Exchange - Документация

## 📋 Содержание

- [Обзор проекта](#обзор-проекта)
- [Архитектура](#архитектура)
- [Быстрый старт](#быстрый-старт)
- [Разработка](#разработка)
- [Деплой](#деплой)
- [Безопасность](#безопасность)
- [Интеграции](#интеграции)

## 🏗️ Обзор проекта

APEX Asia Property Exchange - это полнофункциональная платформа для управления недвижимостью в Азии, включающая:

- **Backend API** (FastAPI + PostgreSQL)
- **Frontend** (Next.js + TypeScript)
- **Admin Panel** (Django)
- **Интеграции** (AmoCRM, Telegram, WhatsApp)

## 🏛️ Архитектура

```
APEX-Asia-Property-EXchange/
├── backend/           # FastAPI API сервер
├── frontend/          # Next.js веб-приложение
├── admin_panel/       # Django админ панель
├── docs/             # Документация
├── k8s/              # Kubernetes манифесты
├── nginx/            # Nginx конфигурации
├── scripts/          # Скрипты развертывания
└── docker-compose*.yml # Docker конфигурации
```

### Технологический стек

- **Backend**: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Admin**: Django, Django REST Framework
- **Infrastructure**: Docker, Kubernetes, Nginx
- **CI/CD**: GitHub Actions

## 🚀 Быстрый старт

### Предварительные требования

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### Локальная разработка

1. **Клонирование репозитория**
```bash
git clone https://github.com/your-org/APEX-Asia-Property-EXchange.git
cd APEX-Asia-Property-EXchange
```

2. **Настройка окружения**
```bash
cp env.example .env
# Отредактируйте .env файл
```

3. **Запуск с Docker**
```bash
# Разработка
docker-compose -f docker-compose.local.yml up -d

# Staging
docker-compose -f docker-compose.staging.yml up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

4. **Проверка работы**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8001
- API Docs: http://localhost:8000/docs

## 💻 Разработка

### Backend разработка

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend разработка

```bash
cd frontend
npm install
npm run dev
```

### Тестирование

```bash
# Backend тесты
cd backend
pytest tests/ -v

# Frontend тесты
cd frontend
npm test

# E2E тесты
npm run test:e2e
```

### Линтинг и форматирование

```bash
# Backend
cd backend
black .
isort .
flake8 .

# Frontend
cd frontend
npm run lint
npm run format
```

## 🚀 Деплой

### Staging

```bash
# Автоматический деплой через GitHub Actions
git push origin develop

# Ручной деплой
./scripts/deploy.sh staging
```

### Production

```bash
# Автоматический деплой через GitHub Actions
git push origin main

# Ручной деплой
./scripts/deploy.sh production
```

### Kubernetes

```bash
# Применение манифестов
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

## 🔒 Безопасность

### Основные принципы

- Все секреты хранятся в GitHub Secrets
- Используется HTTPS везде
- Регулярные обновления зависимостей
- Сканирование уязвимостей в CI/CD

### Проверка безопасности

```bash
# Сканирование зависимостей
cd backend
safety check

cd frontend
npm audit

# Сканирование Docker образов
trivy image your-image:tag
```

## 🔗 Интеграции

### AmoCRM

- Автоматическая синхронизация лидов
- Создание сделок
- Обновление статусов

### Telegram Bot

- Уведомления о новых лидах
- Статус сделок
- Быстрые ответы

### WhatsApp

- Отправка уведомлений
- Автоматические сообщения
- Интеграция с CRM

## 📚 Дополнительная документация

- [Архитектура](./architecture/README.md)
- [API Endpoints](./project/endpoints.md)
- [Интеграции](./integrations/README.md)
- [Безопасность](./SECURITY.md)
- [Changelog](./CHANGELOG.md)

## 🤝 Участие в разработке

1. Fork репозитория
2. Создайте feature ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](../LICENSE) для деталей.

## 📞 Поддержка

- **Email**: support@apex-asia.com
- **Telegram**: @apex_support
- **Issues**: [GitHub Issues](https://github.com/your-org/APEX-Asia-Property-EXchange/issues)
