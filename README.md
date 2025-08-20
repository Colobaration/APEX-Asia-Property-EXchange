# Asia Deals CRM Integration

Полная интеграция amoCRM с лендингом и аналитикой для проекта Asia Deals.

## О проекте

**Asia Deals CRM Integration** - это комплексное решение для автоматизации продаж недвижимости в Азии. Проект включает:

- 🏠 **Лендинг** - привлечение клиентов через рекламные кампании
- 📊 **CRM интеграция** - автоматическая обработка лидов в amoCRM
- 📈 **Аналитика** - метрики CPL, CR, ROI и дашборды
- 🤖 **Автоматизация** - email и WhatsApp воронки
- 🔄 **Webhooks** - синхронизация данных в реальном времени

## Архитектура

### Frontend (Next.js)
- **Лендинг** - привлечение и конвертация посетителей
- **CRM Dashboard** - управление сделками и аналитика
- **Lead Form** - форма приема лидов с UTM-метками
- **Analytics** - визуализация метрик и отчетов

### Backend (FastAPI)
- **API для лидов** - валидация и создание в amoCRM
- **OAuth2 интеграция** - авторизация с amoCRM
- **Webhooks обработка** - синхронизация изменений
- **Аналитические API** - расчет CPL, CR, ROI

### Integrations
- **amoCRM SDK** - Python-обертка над API
- **Email воронки** - автоматические рассылки
- **WhatsApp API** - уведомления и коммуникация

### Analytics
- **Metabase дашборды** - визуализация данных
- **Pipeline скрипты** - расчет метрик
- **Отчеты** - автоматическая генерация

## Чек-лист внедрения

### 1. Настройка окружения
- [ ] Клонирование репозитория
- [ ] Настройка переменных окружения
- [ ] Установка Docker и Docker Compose

### 2. База данных
- [ ] Создание PostgreSQL базы
- [ ] Применение миграций
- [ ] Настройка резервного копирования

### 3. amoCRM интеграция
- [ ] Создание приложения в amoCRM
- [ ] Настройка OAuth2 авторизации
- [ ] Конфигурация webhooks
- [ ] Создание кастомных полей

### 4. Frontend развертывание
- [ ] Настройка домена
- [ ] Конфигурация SSL сертификатов
- [ ] Оптимизация производительности

### 5. Backend развертывание
- [ ] Настройка сервера
- [ ] Конфигурация nginx
- [ ] Настройка мониторинга

### 6. Email интеграция
- [ ] Настройка SMTP сервера
- [ ] Создание email шаблонов
- [ ] Тестирование рассылок

### 7. WhatsApp интеграция
- [ ] Подключение WhatsApp Business API
- [ ] Настройка webhook'ов
- [ ] Создание шаблонов сообщений

### 8. Аналитика
- [ ] Настройка Metabase
- [ ] Создание дашбордов
- [ ] Настройка алертов

### 9. Тестирование
- [ ] Unit тесты
- [ ] Integration тесты
- [ ] E2E тестирование
- [ ] Нагрузочное тестирование

### 10. Мониторинг
- [ ] Настройка логирования
- [ ] Мониторинг ошибок
- [ ] Алерты и уведомления

## Воронка Asia Deals

### Этапы воронки:
1. **Новый лид** - первичный контакт
2. **Первичный контакт** - звонок менеджера
3. **Презентация** - показ объектов
4. **Выбор объекта** - клиент выбрал недвижимость
5. **Резервирование** - внесение депозита
6. **Сделка** - закрытие сделки
7. **Завершено** - успешная сделка

### Автоматизация:
- Email воронка (3 письма)
- WhatsApp уведомления
- Автоматическое назначение менеджеров
- Расчет комиссий

## Модель данных

### Lead (Лид)
```sql
- id (Primary Key)
- name (Имя клиента)
- phone (Телефон)
- email (Email)
- utm_source, utm_medium, utm_campaign, utm_content, utm_term
- amocrm_contact_id, amocrm_lead_id
- status, source
- cost, revenue
- created_at, updated_at
```

### Deal (Сделка)
```sql
- id (Primary Key)
- lead_id (Foreign Key)
- amocrm_deal_id
- amount (Сумма сделки)
- commission, commission_percent
- status, stage
- created_at, updated_at, closed_at
```

## Запуск проекта

### Локальная разработка
```bash
# Клонирование репозитория
git clone <repository-url>
cd asia-deals-crm

# Копирование переменных окружения
cp env.example .env
# Редактирование .env файла

# Запуск всех сервисов
docker-compose up --build

# Доступ к сервисам:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Metabase: http://localhost:3001
# PostgreSQL: localhost:5432
```

### Продакшн развертывание
```bash
# Настройка продакшн переменных
export NODE_ENV=production
export DATABASE_URL=postgresql://user:pass@host:5432/db

# Запуск с продакшн конфигурацией
docker-compose -f docker-compose.prod.yml up -d
```

## Git Flow

### Ветки
- `main` - продакшн код
- `dev` - разработка
- `feature/*` - новые функции
- `hotfix/*` - срочные исправления

### Процесс разработки
1. Создание feature ветки от `dev`
2. Разработка и тестирование
3. Pull Request в `dev`
4. Code Review
5. Merge в `dev`
6. Периодический merge `dev` в `main`

## Роли команды

### dev1 (Backend/Integrations)
- FastAPI разработка
- amoCRM интеграция
- База данных и миграции
- API документация
- Тестирование backend

### dev2 (Frontend/Analytics)
- Next.js разработка
- UI/UX компоненты
- Metabase дашборды
- Email/WhatsApp воронки
- E2E тестирование

## Документация

Подробная документация находится в папке `/docs`:

- [Project Structure](./docs/project-structure.md) - полная структура проекта
- [API Endpoints](./docs/endpoints.md) - описание всех API
- [CRM Fields](./docs/crm-fields.md) - маппинг полей amoCRM
- [Pipelines](./docs/pipelines.md) - воронка продаж
- [Test Plan](./docs/test-plan.md) - план тестирования

## Технологии

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- React Query
- Recharts

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- Pytest

### DevOps
- Docker
- Docker Compose
- nginx
- Metabase
- GitHub Actions

### Интеграции
- amoCRM API
- WhatsApp Business API
- SMTP (Email)
- UTM tracking

## Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## Поддержка

По вопросам поддержки обращайтесь:
- Email: support@asiadeals.com
- Telegram: @asiadeals_support
- Документация: [docs.asiadeals.com](https://docs.asiadeals.com)
