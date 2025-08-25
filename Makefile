# APEX Asia Property Exchange - Makefile

.PHONY: help install dev test clean docker-up docker-down logs

# Переменные
PYTHON_VERSION := 3.11
NODE_VERSION := 18

help: ## Показать справку
	@echo "APEX Asia Property Exchange - Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установка зависимостей
	@echo "📦 Установка зависимостей..."
	cd backend && python -m pip install -r requirements.txt
	cd frontend && npm install

dev: ## Запуск в режиме разработки
	@echo "🚀 Запуск в режиме разработки..."
	docker-compose -f docker-compose.local.yml up -d

staging: ## Запуск staging окружения
	@echo "🚀 Запуск staging окружения..."
	docker-compose -f docker-compose.staging.yml up -d

prod: ## Запуск production окружения
	@echo "🚀 Запуск production окружения..."
	docker-compose -f docker-compose.prod.yml up -d

stop: ## Остановка всех сервисов
	@echo "🛑 Остановка сервисов..."
	docker-compose down

logs: ## Просмотр логов
	@echo "📋 Просмотр логов..."
	docker-compose logs -f

test: ## Запуск всех тестов
	@echo "🧪 Запуск тестов..."
	cd backend && pytest tests/ -v
	cd frontend && npm test

test-backend: ## Тестирование backend
	@echo "🧪 Тестирование backend..."
	cd backend && pytest tests/ -v

test-frontend: ## Тестирование frontend
	@echo "🧪 Тестирование frontend..."
	cd frontend && npm test

lint: ## Проверка кода
	@echo "🔍 Проверка кода..."
	cd backend && black . && isort . && flake8 .
	cd frontend && npm run lint

format: ## Форматирование кода
	@echo "🎨 Форматирование кода..."
	cd backend && black . && isort .
	cd frontend && npm run format

clean: ## Очистка
	@echo "🧹 Очистка..."
	docker-compose down -v
	docker system prune -f
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Сборка Docker образов
	@echo "🏗️ Сборка образов..."
	docker-compose build

deploy-staging: ## Деплой в staging
	@echo "🚀 Деплой в staging..."
	./scripts/deploy.sh staging

deploy-production: ## Деплой в production
	@echo "🚀 Деплой в production..."
	./scripts/deploy.sh production

migrate: ## Применение миграций
	@echo "🗄️ Применение миграций..."
	cd backend && alembic upgrade head

migrate-create: ## Создание миграции
	@echo "🗄️ Создание миграции..."
	cd backend && alembic revision --autogenerate -m "$(message)"

shell: ## Запуск shell
	@echo "🐍 Запуск shell..."
	cd backend && python -c "from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"

status: ## Статус сервисов
	@echo "📊 Статус сервисов..."
	docker-compose ps

restart: ## Перезапуск сервисов
	@echo "🔄 Перезапуск сервисов..."
	docker-compose restart

backup: ## Создание резервной копии
	@echo "💾 Создание резервной копии..."
	docker-compose exec db pg_dump -U asia asia_crm > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore: ## Восстановление из резервной копии
	@echo "💾 Восстановление из резервной копии..."
	docker-compose exec -T db psql -U asia asia_crm < $(file)

# Команды для разработки
dev-backend: ## Запуск только backend
	@echo "🔧 Запуск backend..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Запуск только frontend
	@echo "🌐 Запуск frontend..."
	cd frontend && npm run dev

dev-admin: ## Запуск только admin panel
	@echo "📊 Запуск admin panel..."
	cd admin_panel && python manage.py runserver 0.0.0.0:8001

# Команды для мониторинга
monitor: ## Мониторинг ресурсов
	@echo "📊 Мониторинг ресурсов..."
	docker stats

health: ## Проверка здоровья сервисов
	@echo "🏥 Проверка здоровья сервисов..."
	curl -f http://localhost:8000/health || echo "Backend недоступен"
	curl -f http://localhost:3000 || echo "Frontend недоступен"
	curl -f http://localhost:8001 || echo "Admin panel недоступен"

# Команды для безопасности
security-check: ## Проверка безопасности
	@echo "🛡️ Проверка безопасности..."
	cd backend && safety check
	cd frontend && npm audit

# Команды для документации
docs: ## Генерация документации
	@echo "📚 Генерация документации..."
	cd backend && pydoc-markdown
	cd frontend && npm run docs

# Команды для CI/CD
ci: ## Запуск CI проверок
	@echo "🔍 Запуск CI проверок..."
	make lint
	make test
	make security-check

# Команды для отладки
debug: ## Отладка
	@echo "🐛 Режим отладки..."
	docker-compose -f docker-compose.local.yml up -d
	docker-compose logs -f

# Команды для очистки данных
reset-db: ## Сброс базы данных
	@echo "🗄️ Сброс базы данных..."
	docker-compose down -v
	docker-compose up -d db
	sleep 10
	make migrate

# Команды для обновления зависимостей
update-deps: ## Обновление зависимостей
	@echo "📦 Обновление зависимостей..."
	cd backend && pip install --upgrade -r requirements.txt
	cd frontend && npm update

# Команды для оптимизации
optimize: ## Оптимизация
	@echo "⚡ Оптимизация..."
	docker system prune -f
	docker image prune -f
	npm cache clean --force

# Команды для экспорта/импорта данных
export-data: ## Экспорт данных
	@echo "📤 Экспорт данных..."
	docker-compose exec db pg_dump -U asia asia_crm > export_$(shell date +%Y%m%d_%H%M%S).sql

import-data: ## Импорт данных
	@echo "📥 Импорт данных..."
	docker-compose exec -T db psql -U asia asia_crm < $(file)

# Команды для работы с Git
git-status: ## Статус Git
	@echo "📋 Статус Git..."
	git status

git-pull: ## Pull изменений
	@echo "📥 Pull изменений..."
	git pull origin main

git-push: ## Push изменений
	@echo "📤 Push изменений..."
	git push origin main

# Команды для работы с переменными окружения
env-check: ## Проверка переменных окружения
	@echo "🔍 Проверка переменных окружения..."
	@if [ -f .env ]; then echo "✅ .env файл найден"; else echo "❌ .env файл не найден"; fi

env-setup: ## Настройка переменных окружения
	@echo "⚙️ Настройка переменных окружения..."
	@if [ ! -f .env ]; then cp env.example .env; echo "✅ .env файл создан"; else echo "⚠️ .env файл уже существует"; fi

