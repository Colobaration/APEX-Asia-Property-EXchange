# 📋 Проект APEX

## 🎯 Обзор

Эта директория содержит документацию по проекту APEX Asia Property Exchange.

## 📁 Структура

```
docs/project/
├── README.md                    # Этот файл - обзор проекта
├── project-structure.md         # Структура проекта
├── endpoints.md                 # API endpoints
├── crm-fields.md               # CRM поля
└── pipelines.md                # Воронка продаж
```

## 📋 Документация по проекту

### **project-structure.md** - Структура проекта
**Назначение:** Подробное описание структуры проекта APEX

**Содержит:**
- ✅ Организация файлов и папок
- ✅ Модули и компоненты
- ✅ Зависимости
- ✅ Конфигурация

**Для кого:** Разработчики, архитекторы

### **endpoints.md** - API endpoints
**Назначение:** Документация всех API endpoints

**Содержит:**
- ✅ REST API endpoints
- ✅ Параметры запросов
- ✅ Примеры ответов
- ✅ Коды ошибок

**Для кого:** Frontend разработчики, интеграторы

### **crm-fields.md** - CRM поля
**Назначение:** Маппинг полей CRM системы

**Содержит:**
- ✅ Поля лидов
- ✅ Поля сделок
- ✅ Кастомные поля
- ✅ Маппинг с AmoCRM

**Для кого:** Разработчики, аналитики

### **pipelines.md** - Воронка продаж
**Назначение:** Описание воронки продаж

**Содержит:**
- ✅ Этапы воронки
- ✅ Метрики
- ✅ Автоматизация
- ✅ Отчеты

**Для кого:** Менеджеры, аналитики

## 🎯 Основные компоненты проекта

### **1. Backend (FastAPI)**
```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Основные настройки
│   ├── models/        # SQLAlchemy модели
│   ├── schemas/       # Pydantic схемы
│   ├── services/      # Бизнес-логика
│   └── integrations/  # Внешние интеграции
├── tests/             # Тесты
├── alembic/           # Миграции БД
└── requirements.txt   # Зависимости
```

### **2. Frontend (Next.js)**
```
frontend/
├── src/
│   ├── components/    # React компоненты
│   ├── pages/         # Страницы
│   ├── hooks/         # React хуки
│   ├── lib/           # Утилиты
│   └── types/         # TypeScript типы
├── public/            # Статические файлы
└── package.json       # Зависимости
```

### **3. Infrastructure**
```
├── docker-compose.yml     # Docker Compose
├── k8s/                   # Kubernetes манифесты
├── nginx/                 # Nginx конфигурации
└── scripts/               # Скрипты развертывания
```

## 🔗 API Endpoints

### **Аутентификация**
```http
POST /api/auth/login
POST /api/auth/register
POST /api/auth/refresh
GET  /api/auth/profile
```

### **Лиды**
```http
GET    /api/leads/
POST   /api/leads/
GET    /api/leads/{id}
PUT    /api/leads/{id}
DELETE /api/leads/{id}
```

### **Аналитика**
```http
GET /api/analytics/dashboard
GET /api/analytics/leads
GET /api/analytics/conversion
GET /api/analytics/revenue
```

### **Webhook'и**
```http
POST /api/webhooks/amocrm
POST /api/webhooks/test
GET  /api/webhooks/status
```

## 📊 CRM Поля

### **Поля лидов**
- `name` - Имя лида
- `email` - Email адрес
- `phone` - Номер телефона
- `source` - Источник лида
- `status` - Статус лида
- `created_at` - Дата создания
- `updated_at` - Дата обновления

### **Поля сделок**
- `lead_id` - ID лида
- `amount` - Сумма сделки
- `currency` - Валюта
- `stage` - Этап сделки
- `probability` - Вероятность закрытия
- `close_date` - Дата закрытия

### **Кастомные поля**
- `utm_source` - UTM источник
- `utm_medium` - UTM канал
- `utm_campaign` - UTM кампания
- `property_type` - Тип недвижимости
- `budget` - Бюджет
- `location` - Локация

## 🔄 Воронка продаж

### **Этапы воронки**
1. **Lead Generation** - Генерация лидов
2. **Lead Qualification** - Квалификация лидов
3. **Proposal** - Предложение
4. **Negotiation** - Переговоры
5. **Closing** - Закрытие сделки

### **Метрики**
- **Conversion Rate** - Конверсия между этапами
- **Lead Velocity** - Скорость генерации лидов
- **Sales Cycle** - Длительность цикла продаж
- **Win Rate** - Процент выигранных сделок

### **Автоматизация**
- Автоматическое создание лидов из форм
- Уведомления о новых лидах
- Назначение ответственных
- Отправка follow-up сообщений

## 🚀 Быстрый старт

### **Запуск проекта**
```bash
# Клонирование
git clone <repository>
cd APEX-Asia-Property-EXchange

# Установка зависимостей
make install

# Запуск в режиме разработки
make dev
```

### **Доступ к сервисам**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Metabase:** http://localhost:3001

## 🔧 Конфигурация

### **Переменные окружения**
```bash
# Основные настройки
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# База данных
DB_URL=postgresql://asia:asia@db:5432/asia_crm

# AmoCRM
AMOCRM_CLIENT_ID=your_client_id
AMOCRM_CLIENT_SECRET=your_client_secret
AMOCRM_DOMAIN=your_domain.amocrm.ru

# Безопасность
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret
```

## 🧪 Тестирование

### **Запуск тестов**
```bash
# Все тесты
make test

# Backend тесты
make test-backend

# Frontend тесты
make test-frontend

# E2E тесты
make test-e2e
```

### **Покрытие кода**
```bash
# Backend coverage
cd backend && pytest --cov=app --cov-report=html

# Frontend coverage
cd frontend && npm run test:coverage
```

## 📊 Мониторинг

### **Health Checks**
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000/

# Database
docker-compose exec db pg_isready -U asia
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

## 🔒 Безопасность

### **Аутентификация**
- JWT токены
- OAuth2 для AmoCRM
- Session management
- Password hashing

### **Авторизация**
- Role-based access control (RBAC)
- Permission-based access
- API key authentication
- Rate limiting

### **Защита данных**
- HTTPS для всех соединений
- Валидация входных данных
- SQL injection protection
- XSS protection

## 📈 Масштабирование

### **Горизонтальное масштабирование**
- Load balancer для API
- Репликация базы данных
- Redis cluster
- CDN для статических файлов

### **Вертикальное масштабирование**
- Увеличение ресурсов серверов
- Оптимизация запросов к БД
- Кэширование
- Асинхронная обработка

## 🔗 Связанная документация

- [Архитектура](../architecture/README.md) - архитектура системы
- [CI/CD документация](../cicd/README.md) - автоматизация
- [Настройка](../setup/README.md) - настройка компонентов
- [Интеграции](../integrations/README.md) - внешние интеграции
- [Быстрый старт](../quickstart/README.md) - быстрый старт

## 📞 Поддержка

При возникновении вопросов:

1. Обратитесь к документации в соответствующих разделах
2. Проверьте логи сервисов
3. Убедитесь в корректности конфигурации
4. Создайте issue в репозитории

---

**Проект APEX готов к работе! 🎉**
