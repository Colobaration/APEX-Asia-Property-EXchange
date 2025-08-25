# APEX Asia Property Exchange

[![CI/CD](https://github.com/your-org/APEX-Asia-Property-EXchange/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/your-org/APEX-Asia-Property-EXchange/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Полнофункциональная платформа для управления недвижимостью в Азии с интеграцией CRM, уведомлениями и аналитикой.

## 🚀 Быстрый старт

```bash
# Клонирование
git clone https://github.com/your-org/APEX-Asia-Property-EXchange.git
cd APEX-Asia-Property-EXchange

# Настройка
cp env.example .env
# Отредактируйте .env

# Запуск
docker-compose -f docker-compose.local.yml up -d
```

**Доступ к сервисам:**
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- 📊 Admin Panel: http://localhost:8001
- 📚 API Docs: http://localhost:8000/docs

## 🏗️ Архитектура

```
├── backend/           # FastAPI API сервер
├── frontend/          # Next.js веб-приложение  
├── admin_panel/       # Django админ панель
├── k8s/              # Kubernetes манифесты
├── nginx/            # Nginx конфигурации
└── docs/             # Документация
```

## 🛠️ Технологии

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Admin**: Django, Django REST Framework
- **Infrastructure**: Docker, Kubernetes, Nginx
- **CI/CD**: GitHub Actions

## 📚 Документация

Подробная документация доступна в папке [docs/](./docs/README.md):

- [Быстрый старт](./docs/README.md#быстрый-старт)
- [Архитектура](./docs/architecture/README.md)
- [API Endpoints](./docs/project/endpoints.md)
- [Интеграции](./docs/integrations/README.md)
- [Безопасность](./docs/SECURITY.md)

## 🔗 Интеграции

- **AmoCRM** - автоматическая синхронизация лидов и сделок
- **Telegram** - уведомления и быстрые ответы
- **WhatsApp** - автоматические сообщения клиентам

## 🧪 Тестирование

```bash
# Backend тесты
cd backend && pytest tests/ -v

# Frontend тесты  
cd frontend && npm test

# E2E тесты
npm run test:e2e
```

## 🚀 Деплой

```bash
# Staging
git push origin develop

# Production
git push origin main
```

## 🤝 Участие в разработке

1. Fork репозитория
2. Создайте feature ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 📞 Поддержка

- **Email**: support@apex-asia.com
- **Telegram**: @apex_support
- **Issues**: [GitHub Issues](https://github.com/your-org/APEX-Asia-Property-EXchange/issues)

---

**APEX Asia Property Exchange** - Управление недвижимостью в Азии стало проще! 🏠✨
