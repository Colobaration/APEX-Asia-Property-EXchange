# APEX Asia Property Exchange - Makefile

.PHONY: help install test lint build deploy clean docker-build docker-push

# Переменные
PROJECT_NAME = apex-asia-property-exchange
VERSION ?= $(shell git rev-parse --short HEAD)
REGISTRY = ghcr.io
IMAGE_NAME = $(shell git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/')

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку
	@echo "$(GREEN)APEX Asia Property Exchange - Команды:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# Установка зависимостей
install: ## Установить все зависимости
	@echo "$(GREEN)Устанавливаем зависимости...$(NC)"
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

# Тестирование
test: ## Запустить все тесты
	@echo "$(GREEN)Запускаем тесты...$(NC)"
	cd backend && pytest tests/ -v --cov=app --cov-report=html
	cd frontend && npm test -- --coverage --watchAll=false

test-backend: ## Тестировать только backend
	@echo "$(GREEN)Тестируем backend...$(NC)"
	cd backend && pytest tests/ -v --cov=app --cov-report=html

test-frontend: ## Тестировать только frontend
	@echo "$(GREEN)Тестируем frontend...$(NC)"
	cd frontend && npm test -- --coverage --watchAll=false

# Линтинг
lint: ## Запустить линтеры
	@echo "$(GREEN)Запускаем линтеры...$(NC)"
	cd backend && black . && isort . && flake8 .
	cd frontend && npm run lint

lint-backend: ## Линтинг backend
	@echo "$(GREEN)Линтинг backend...$(NC)"
	cd backend && black . && isort . && flake8 .

lint-frontend: ## Линтинг frontend
	@echo "$(GREEN)Линтинг frontend...$(NC)"
	cd frontend && npm run lint

# Сборка
build: ## Собрать все компоненты
	@echo "$(GREEN)Собираем проект...$(NC)"
	cd frontend && npm run build

# Docker команды
docker-build: ## Собрать Docker образы
	@echo "$(GREEN)Собираем Docker образы...$(NC)"
	docker build -t $(REGISTRY)/$(IMAGE_NAME)-backend:$(VERSION) ./backend
	docker build -t $(REGISTRY)/$(IMAGE_NAME)-frontend:$(VERSION) ./frontend

docker-push: ## Отправить Docker образы в registry
	@echo "$(GREEN)Отправляем Docker образы...$(NC)"
	docker push $(REGISTRY)/$(IMAGE_NAME)-backend:$(VERSION)
	docker push $(REGISTRY)/$(IMAGE_NAME)-frontend:$(VERSION)

# Простой деплой (без Kubernetes)
deploy-staging: ## Деплой в staging
	@echo "$(GREEN)Деплоим в staging...$(NC)"
	./scripts/deploy-simple.sh staging $(VERSION)

deploy-production: ## Деплой в production
	@echo "$(GREEN)Деплоим в production...$(NC)"
	./scripts/deploy-simple.sh production $(VERSION)

# Docker Compose команды
dev: ## Запустить в режиме разработки
	@echo "$(GREEN)Запускаем в режиме разработки...$(NC)"
	docker-compose up -d

dev-stop: ## Остановить режим разработки
	@echo "$(GREEN)Останавливаем режим разработки...$(NC)"
	docker-compose down

staging: ## Запустить staging окружение
	@echo "$(GREEN)Запускаем staging окружение...$(NC)"
	TAG=$(VERSION) docker-compose -f docker-compose.staging.yml up -d

staging-stop: ## Остановить staging окружение
	@echo "$(GREEN)Останавливаем staging окружение...$(NC)"
	docker-compose -f docker-compose.staging.yml down

production: ## Запустить production окружение
	@echo "$(GREEN)Запускаем production окружение...$(NC)"
	TAG=$(VERSION) docker-compose -f docker-compose.prod.yml up -d

production-stop: ## Остановить production окружение
	@echo "$(GREEN)Останавливаем production окружение...$(NC)"
	docker-compose -f docker-compose.prod.yml down

# Мониторинг
status: ## Показать статус всех сервисов
	@echo "$(GREEN)Статус сервисов:$(NC)"
	@echo "Development:"
	docker-compose ps
	@echo ""
	@echo "Staging:"
	docker-compose -f docker-compose.staging.yml ps
	@echo ""
	@echo "Production:"
	docker-compose -f docker-compose.prod.yml ps

logs: ## Показать логи development
	@echo "$(GREEN)Логи development:$(NC)"
	docker-compose logs -f

logs-staging: ## Показать логи staging
	@echo "$(GREEN)Логи staging:$(NC)"
	docker-compose -f docker-compose.staging.yml logs -f

logs-production: ## Показать логи production
	@echo "$(GREEN)Логи production:$(NC)"
	docker-compose -f docker-compose.prod.yml logs -f

# CI/CD
ci-test: ## Запустить тесты для CI
	@echo "$(GREEN)Запускаем CI тесты...$(NC)"
	cd backend && pytest tests/ -v --cov=app --cov-report=xml
	cd frontend && npm test -- --coverage --watchAll=false --coverageReporters=lcov

ci-lint: ## Запустить линтеры для CI
	@echo "$(GREEN)Запускаем CI линтеры...$(NC)"
	cd backend && black --check . && isort --check-only . && flake8 .
	cd frontend && npm run lint

# Безопасность
security-scan: ## Сканирование безопасности
	@echo "$(GREEN)Сканируем на уязвимости...$(NC)"
	cd backend && safety check
	cd frontend && npm audit

# Мониторинг
monitor: ## Мониторинг приложения
	@echo "$(GREEN)Мониторинг приложения:$(NC)"
	@echo "Development Backend health:"
	curl -s http://localhost:8000/health || echo "Backend недоступен"
	@echo "Development Frontend:"
	curl -s http://localhost:3000/ | head -1 || echo "Frontend недоступен"

monitor-staging: ## Мониторинг staging
	@echo "$(GREEN)Мониторинг staging:$(NC)"
	@echo "Staging Backend health:"
	curl -s http://localhost:8001/health || echo "Backend недоступен"
	@echo "Staging Frontend:"
	curl -s http://localhost:3001/ | head -1 || echo "Frontend недоступен"

# Создание релиза
release: ## Создать новый релиз
	@echo "$(GREEN)Создаем релиз...$(NC)"
	@read -p "Введите версию (например, v1.2.3): " version; \
	git tag $$version; \
	git push origin $$version; \
	echo "Релиз $$version создан и отправлен"

# Полная проверка перед деплоем
pre-deploy: install lint test security-scan ## Полная проверка перед деплоем
	@echo "$(GREEN)Все проверки пройдены! Готов к деплою.$(NC)"

# Очистка
clean: ## Очистить временные файлы
	@echo "$(GREEN)Очищаем временные файлы...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	cd frontend && rm -rf node_modules .next coverage
	cd backend && rm -rf htmlcov .pytest_cache

clean-all: ## Очистить все контейнеры и образы
	@echo "$(RED)Очищаем все контейнеры и образы...$(NC)"
	docker-compose down -v
	docker-compose -f docker-compose.staging.yml down -v
	docker-compose -f docker-compose.prod.yml down -v
	docker system prune -af

# Резервное копирование
backup: ## Создать резервную копию БД
	@echo "$(GREEN)Создаем резервную копию БД...$(NC)"
	docker exec asia-db pg_dump -U asia asia_crm > backup_$(shell date +%Y%m%d_%H%M%S).sql

backup-staging: ## Создать резервную копию staging БД
	@echo "$(GREEN)Создаем резервную копию staging БД...$(NC)"
	docker exec asia-db-staging pg_dump -U asia asia_crm_staging > backup_staging_$(shell date +%Y%m%d_%H%M%S).sql

# Восстановление
restore: ## Восстановить БД из резервной копии
	@echo "$(RED)Восстановление БД из резервной копии...$(NC)"
	@read -p "Введите имя файла резервной копии: " file; \
	docker exec -T asia-db psql -U asia asia_crm < $$file

restore-staging: ## Восстановить staging БД из резервной копии
	@echo "$(RED)Восстановление staging БД из резервной копии...$(NC)"
	@read -p "Введите имя файла резервной копии: " file; \
	docker exec -T asia-db-staging psql -U asia asia_crm_staging < $$file

