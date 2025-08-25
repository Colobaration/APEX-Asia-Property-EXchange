# 🔌 Конфигурация портов APEX Asia Property Exchange

## 📊 Сравнение портов по окружениям

### 🛠️ Development (docker-compose.yml)
| Сервис | Порт хоста | Порт контейнера | URL |
|--------|------------|-----------------|-----|
| Backend API | 8000 | 8000 | http://localhost:8000 |
| Frontend | 3001 | 3000 | http://localhost:3001 |
| Admin Panel | 8003 | 8000 | http://localhost:8003 |
| PostgreSQL | 5432 | 5432 | localhost:5432 |
| Redis | 6379 | 6379 | localhost:6379 |

### 🧪 Staging (docker-compose.staging.yml)
| Сервис | Порт хоста | Порт контейнера | URL |
|--------|------------|-----------------|-----|
| Backend API | 8001 | 8000 | http://localhost:8001 |
| Frontend | 3000 | 3000 | http://localhost:3000 |
| Admin Panel | 8002 | 8000 | http://localhost:8002 |
| PostgreSQL | 5433 | 5432 | localhost:5433 |
| Redis | 6380 | 6379 | localhost:6380 |

## 🚀 Запуск окружений

### Development
```bash
# Запуск development окружения
docker-compose up -d

# Доступ к сервисам:
# Backend: http://localhost:8000
# Frontend: http://localhost:3001
# Admin Panel: http://localhost:8003
# Database: localhost:5432
# Redis: localhost:6379
```

### Staging
```bash
# Запуск staging окружения
docker-compose -f docker-compose.staging.yml up -d

# Доступ к сервисам:
# Backend: http://localhost:8001
# Frontend: http://localhost:3000
# Admin Panel: http://localhost:8002
# Database: localhost:5433
# Redis: localhost:6380
```

## 🔧 Конфигурация окружений

### Development
- **Environment**: development
- **Debug**: True
- **Log Level**: DEBUG
- **Database**: asia_crm_dev
- **Auto Migrations**: True
- **Auto Init DB**: True

### Staging
- **Environment**: staging
- **Debug**: False
- **Log Level**: WARNING
- **Database**: asia_crm_staging
- **Auto Migrations**: False
- **Auto Init DB**: False

## 🌐 Домены

### Development
- Backend API: `api.dev.apex-asia.com`
- Frontend: `dev.apex-asia.com`
- Admin Panel: `admin.dev.apex-asia.com`

### Staging
- Backend API: `api.staging.apex-asia.com`
- Frontend: `staging.apex-asia.com`
- Admin Panel: `admin.staging.apex-asia.com`

## 📝 Примечания

### ✅ Преимущества новой конфигурации:
1. **Нет конфликтов портов** между окружениями
2. **Четкое разделение** development и staging
3. **Уникальные имена контейнеров** для каждого окружения
4. **Отдельные volumes** для данных
5. **Разные сети** для изоляции

### 🔍 Мониторинг:
- **Development**: Все сервисы доступны на стандартных портах
- **Staging**: Сервисы на смещенных портах для избежания конфликтов

### 🛡️ Безопасность:
- Разные секретные ключи для каждого окружения
- Изолированные базы данных
- Отдельные Redis инстансы

## 🚨 Важные моменты

1. **Не запускайте оба окружения одновременно** на одном хосте
2. **Проверяйте занятость портов** перед запуском
3. **Используйте правильные переменные окружения** для каждого сервиса
4. **Мониторьте логи** для диагностики проблем

## 🔄 Миграция

При необходимости изменить порты:

1. Обновите соответствующий `docker-compose.yml`
2. Измените переменные окружения
3. Обновите документацию
4. Уведомите команду о изменениях
