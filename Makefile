# APEX Asia Property Exchange - Main Makefile
# Управление всем проектом

.PHONY: help dev install lint format test build clean docker-up docker-down docker-build docker-logs

help: ## Показать справку
	@echo "APEX Asia Property Exchange - Project Management"
	@echo "==============================================="
	@echo ""
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Установка зависимостей
install: ## Установить зависимости для всех сервисов
	@echo "📦 Установка зависимостей для всех сервисов..."
	@echo "Backend..."
	@cd backend && make install
	@echo "Frontend..."
	@cd frontend && make install
	@echo "✅ Все зависимости установлены"

# Разработка
dev: ## Запустить все сервисы в режиме разработки
	@echo "🚀 Запуск всех сервисов в режиме разработки..."
	docker-compose up -d db redis
	@echo "⏳ Ожидание готовности базы данных..."
	@sleep 10
	@echo "Backend..."
	@cd backend && make dev &
	@echo "Frontend..."
	@cd frontend && make dev &
	@echo "✅ Все сервисы запущены"
	@echo "📱 Frontend: http://localhost:3000"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📊 API Docs: http://localhost:8000/docs"

# Линтинг и форматирование
lint: ## Проверить код линтерами
	@echo "🔍 Проверка кода..."
	@echo "Backend..."
	@cd backend && make lint
	@echo "Frontend..."
	@cd frontend && make lint
	@echo "✅ Линтинг завершен"

lint-fix: ## Исправить ошибки линтера
	@echo "🔧 Исправление ошибок линтера..."
	@echo "Backend..."
	@cd backend && make format
	@echo "Frontend..."
	@cd frontend && make lint-fix
	@echo "✅ Ошибки исправлены"

format: ## Форматировать код
	@echo "✨ Форматирование кода..."
	@echo "Backend..."
	@cd backend && make format
	@echo "Frontend..."
	@cd frontend && make format
	@echo "✅ Форматирование завершено"

# Тестирование
test: ## Запустить тесты
	@echo "🧪 Запуск тестов..."
	@echo "Backend..."
	@cd backend && make test
	@echo "Frontend..."
	@cd frontend && make test
	@echo "✅ Тестирование завершено"

test-coverage: ## Запустить тесты с покрытием
	@echo "📊 Запуск тестов с покрытием..."
	@echo "Backend..."
	@cd backend && make test
	@echo "Frontend..."
	@cd frontend && make test-coverage
	@echo "✅ Тестирование с покрытием завершено"

# Сборка
build: ## Собрать все сервисы
	@echo "🏗️ Сборка всех сервисов..."
	@echo "Backend..."
	@cd backend && make docker-build
	@echo "Frontend..."
	@cd frontend && make docker-build
	@echo "✅ Сборка завершена"

# Docker команды
docker-up: ## Запустить все сервисы в Docker
	@echo "🐳 Запуск всех сервисов в Docker..."
	docker-compose up -d
	@echo "✅ Сервисы запущены"
	@echo "📱 Frontend: http://localhost:3000"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📊 API Docs: http://localhost:8000/docs"

docker-down: ## Остановить все сервисы в Docker
	@echo "🛑 Остановка всех сервисов в Docker..."
	docker-compose down
	@echo "✅ Сервисы остановлены"

docker-build: ## Собрать все Docker образы
	@echo "🐳 Сборка всех Docker образов..."
	docker-compose build
	@echo "✅ Образы собраны"

docker-logs: ## Показать логи Docker сервисов
	@echo "📋 Логи Docker сервисов..."
	docker-compose logs -f

# Очистка
clean: ## Очистить временные файлы
	@echo "🧹 Очистка временных файлов..."
	@echo "Backend..."
	@cd backend && make clean
	@echo "Frontend..."
	@cd frontend && make clean
	@echo "Docker..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Очистка завершена"

# Миграции базы данных
migrate: ## Выполнить миграции базы данных
	@echo "🔄 Выполнение миграций..."
	@cd backend && make migrate

migrate-status: ## Показать статус миграций
	@echo "📊 Статус миграций..."
	@cd backend && make migrate-status

# Проверки
check-all: ## Выполнить все проверки
	@echo "🔍 Выполнение всех проверок..."
	@echo "Backend..."
	@cd backend && make lint
	@echo "Frontend..."
	@cd frontend && make check-all
	@echo "✅ Все проверки пройдены"

# CI/CD
ci: ## Команды для CI/CD
	@echo "🤖 Выполнение CI/CD команд..."
	@echo "Backend..."
	@cd backend && make lint
	@echo "Frontend..."
	@cd frontend && make ci
	@echo "✅ CI/CD команды выполнены"

# Информация
info: ## Показать информацию о проекте
	@echo "📋 Информация о проекте:"
	@echo "  • Backend: FastAPI + SQLAlchemy + PostgreSQL"
	@echo "  • Frontend: Next.js + TypeScript + Tailwind"
	@echo "  • Database: PostgreSQL"
	@echo "  • Cache: Redis"
	@echo "  • Containerization: Docker + Docker Compose"
	@echo "  • CI/CD: GitHub Actions"
	@echo ""
	@echo "Полезные команды:"
	@echo "  • make dev          - Запуск в режиме разработки"
	@echo "  • make docker-up    - Запуск в Docker"
	@echo "  • make test         - Запуск тестов"
	@echo "  • make lint         - Проверка кода"
	@echo "  • make migrate      - Миграции БД"

# Быстрый старт
quick-start: ## Быстрый старт проекта
	@echo "⚡ Быстрый старт проекта..."
	@make install
	@make docker-up
	@echo "✅ Проект запущен!"
	@echo "📱 Frontend: http://localhost:3000"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📊 API Docs: http://localhost:8000/docs"

