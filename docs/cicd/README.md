# 🚀 CI/CD Документация APEX

## 🎯 Обзор

Эта директория содержит всю документацию по CI/CD (Continuous Integration/Continuous Deployment) для проекта APEX Asia Property Exchange.

## 📁 Структура документации

```
docs/cicd/
├── README.md                    # Этот файл - главная документация
├── ci-cd-setup.md              # Подробная настройка CI/CD
├── simple/                     # Упрощенная версия CI/CD
│   └── README-CI-CD-SIMPLE.md  # Документация простой версии
├── kubernetes/                 # Kubernetes версия CI/CD
│   └── README-CI-CD.md         # Документация Kubernetes версии
├── guides/                     # Руководства и инструкции
│   ├── TEST_CI_CD.md           # Тестирование CI/CD
│   ├── QUICK_SETUP_GUIDE.md    # Быстрая настройка
│   ├── GITHUB_SETUP_PROMPT.md  # Настройка GitHub
│   ├── CREATE_PR_INSTRUCTIONS.md # Инструкции по PR
│   └── PR_DESCRIPTION.md       # Шаблоны PR
└── scripts/                    # Документация скриптов
    └── README.md               # Описание скриптов деплоя
```

## 🚀 Варианты CI/CD

### **1. Простая версия (Docker Compose)**
**Рекомендуется для:** небольших проектов, быстрого старта

**Преимущества:**
- ✅ Простая настройка
- ✅ Минимальные требования к серверу
- ✅ Быстрый деплой
- ✅ Легкое понимание

**Файлы:**
- `simple/README-CI-CD-SIMPLE.md` - документация
- `.github/workflows/ci-cd-simple.yml` - workflow
- `scripts/deploy-simple.sh` - скрипт деплоя

**Использование:**
```bash
# Деплой в staging
./scripts/deploy-simple.sh staging

# Деплой в production
./scripts/deploy-simple.sh production
```

### **2. Kubernetes версия**
**Рекомендуется для:** production окружений, масштабируемых проектов

**Преимущества:**
- ✅ Высокая масштабируемость
- ✅ Отказоустойчивость
- ✅ Продвинутое управление
- ✅ Blue-green деплой

**Файлы:**
- `kubernetes/README-CI-CD.md` - документация
- `.github/workflows/ci-cd.yml` - workflow
- `.github/workflows/deploy-kubernetes.yml` - ручной деплой
- `scripts/deploy.sh` - скрипт деплоя
- `k8s/` - Kubernetes манифесты

**Использование:**
```bash
# Деплой в staging
./scripts/deploy.sh staging

# Деплой в production
./scripts/deploy.sh production
```

## 🔄 Workflow процессы

### **Автоматический деплой**

| Действие | Ветка | Результат |
|----------|-------|-----------|
| Push в `develop` | develop | Деплой в staging |
| Push в `main` | main | Деплой в production |
| Pull Request | любая | Только тестирование |

### **Ручной деплой**

```bash
# Простая версия
./scripts/deploy-simple.sh staging
./scripts/deploy-simple.sh production

# Kubernetes версия
./scripts/deploy.sh staging
./scripts/deploy.sh production
```

## 🛠️ Команды Makefile

### **Основные команды**
```bash
# Деплой
make deploy-staging
make deploy-production

# Тестирование
make test
make test-backend
make test-frontend

# Линтинг
make lint
make lint-backend
make lint-frontend

# Сборка
make docker-build
make docker-push

# Мониторинг
make status
make logs
make logs-staging
make logs-production
```

### **Безопасность**
```bash
# Сканирование безопасности
make security-scan

# Резервное копирование
make backup
make backup-staging
```

## 🔒 Безопасность

### **Сканирование уязвимостей**
- **Python**: `safety` для проверки зависимостей
- **Node.js**: `npm audit` для проверки пакетов
- **Docker**: `Trivy` для сканирования образов
- **Автоматическое**: каждую неделю в понедельник

### **Секреты**
- Переменные окружения в `.env` файлах
- GitHub Secrets для CI/CD
- SSL сертификаты для production

## 📊 Мониторинг

### **Health Checks**
- Backend: `GET /health`
- Frontend: `GET /`
- Database: PostgreSQL readiness
- Redis: Ping проверка

### **Логи**
```bash
# Логи development
make logs

# Логи staging
make logs-staging

# Логи production
make logs-production
```

### **Статус сервисов**
```bash
# Статус всех окружений
make status

# Статус development
docker-compose ps

# Статус staging
docker-compose -f docker-compose.staging.yml ps

# Статус production
docker-compose -f docker-compose.prod.yml ps
```

## 🔄 Откат деплоя

### **Автоматический откат**
1. Перейдите в GitHub Actions
2. Выберите "Rollback Deployment"
3. Выберите окружение и версию
4. Нажмите "Run workflow"

### **Ручной откат**

**Простая версия:**
```bash
# Остановить текущие контейнеры
docker-compose -f docker-compose.prod.yml down

# Запустить предыдущую версию
TAG=v1.2.2 docker-compose -f docker-compose.prod.yml up -d
```

**Kubernetes версия:**
```bash
# Откат последнего деплоя
kubectl rollout undo deployment/backend -n production
kubectl rollout undo deployment/frontend -n production

# Откат к конкретной версии
kubectl set image deployment/backend backend=ghcr.io/your-repo/backend:v1.2.2 -n production
kubectl set image deployment/frontend frontend=ghcr.io/your-repo/frontend:v1.2.2 -n production
```

## 🚨 Troubleshooting

### **Частые проблемы**

1. **Ошибка сборки образа**
   ```bash
   # Проверьте Dockerfile
   docker build -t test ./backend
   
   # Проверьте зависимости
   make install
   ```

2. **Ошибка деплоя**
   ```bash
   # Проверьте Docker и Docker Compose
   docker --version
   docker-compose --version
   
   # Проверьте доступ к registry
   docker pull ghcr.io/your-repo/backend:latest
   ```

3. **Сервис не отвечает**
   ```bash
   # Проверьте статус контейнеров
   make status
   
   # Проверьте логи
   make logs
   
   # Проверьте health checks
   curl http://localhost:8000/health
   curl http://localhost:3000/
   ```

### **Полезные команды**
```bash
# Подключение к контейнеру
docker exec -it asia-backend bash
docker exec -it asia-frontend bash

# Просмотр переменных окружения
docker exec asia-backend env

# Перезапуск сервиса
docker-compose restart backend
docker-compose restart frontend

# Очистка
make clean-all
```

## 📈 Метрики и аналитика

### **Code Coverage**
- Backend: генерируется в `backend/htmlcov/`
- Frontend: генерируется в `frontend/coverage/`
- Отправляется в Codecov

### **Время деплоя**
- Staging: ~3-5 минут
- Production: ~5-8 минут

### **Уведомления**
- Slack уведомления о статусе деплоя
- GitHub Actions статус в репозитории

## 🔧 Настройка для новых проектов

1. Скопируйте файлы CI/CD в ваш проект
2. Обновите переменные в `.github/variables.env`
3. Настройте GitHub Secrets
4. Обновите домены в конфигурациях
5. Протестируйте pipeline

## 🆚 Сравнение версий

| Функция | Простая версия | Kubernetes версия |
|---------|----------------|-------------------|
| Сложность настройки | 🟢 Низкая | 🔴 Высокая |
| Масштабируемость | 🟡 Средняя | 🟢 Высокая |
| Отказоустойчивость | 🟡 Средняя | 🟢 Высокая |
| Мониторинг | 🟢 Простой | 🟢 Продвинутый |
| Обновления | 🟢 Простые | 🟢 Продвинутые |
| Требования к серверу | 🟢 Минимальные | 🔴 Высокие |

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи GitHub Actions
2. Проверьте статус Docker контейнеров
3. Обратитесь к документации в соответствующих папках
4. Создайте issue в репозитории

## 🔮 Будущее развитие

### **Планируемые улучшения:**
1. **Blue-Green деплой** - нулевое время простоя
2. **Canary деплой** - постепенное развертывание
3. **Автоматический rollback** - при ошибках
4. **Мониторинг деплоя** - метрики и алерты
5. **Multi-region деплой** - географическое распределение

---

**Удачного деплоя! 🚀**
