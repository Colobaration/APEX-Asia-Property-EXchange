# Makefile для APEX Asia Property Exchange

.PHONY: help install start stop restart logs test clean migrate

# Переменные
DOCKER_COMPOSE = docker-compose
PYTHON = python3
PIP = pip3

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку
	@echo "$(GREEN)APEX Asia Property Exchange - Команды управления$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(PIP) install -r backend/requirements.txt
	cd frontend && npm install

start: ## Запустить приложение
	@echo "$(GREEN)Запуск приложения...$(NC)"
	$(DOCKER_COMPOSE) up -d

stop: ## Остановить приложение
	@echo "$(YELLOW)Остановка приложения...$(NC)"
	$(DOCKER_COMPOSE) down

restart: stop start ## Перезапустить приложение

logs: ## Показать логи
	@echo "$(GREEN)Логи приложения:$(NC)"
	$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## Показать логи frontend
	@echo "$(GREEN)Логи frontend:$(NC)"
	$(DOCKER_COMPOSE) logs -f frontend

logs-db: ## Показать логи базы данных
	@echo "$(GREEN)Логи базы данных:$(NC)"
	$(DOCKER_COMPOSE) logs -f db

test: ## Запустить тесты
	@echo "$(GREEN)Запуск тестов...$(NC)"
	cd backend && $(PYTHON) -m pytest tests/

test-integration: ## Запустить тесты интеграции
	@echo "$(GREEN)Запуск тестов интеграции amoCRM...$(NC)"
	$(PYTHON) scripts/test_amocrm_integration.py

migrate: ## Запустить миграции БД
	@echo "$(GREEN)Запуск миграций...$(NC)"
	cd backend && $(PYTHON) -m alembic upgrade head

migrate-create: ## Создать новую миграцию
	@echo "$(GREEN)Создание новой миграции...$(NC)"
	@read -p "Введите название миграции: " name; \
	cd backend && $(PYTHON) -m alembic revision --autogenerate -m "$$name"

clean: ## Очистить проект
	@echo "$(RED)Очистка проекта...$(NC)"
	$(DOCKER_COMPOSE) down -v
	docker system prune -f
	rm -rf backend/__pycache__
	rm -rf frontend/node_modules

setup: install migrate start ## Полная настройка проекта

status: ## Показать статус сервисов
	@echo "$(GREEN)Статус сервисов:$(NC)"
	$(DOCKER_COMPOSE) ps

health: ## Проверить здоровье приложения
	@echo "$(GREEN)Проверка здоровья приложения:$(NC)"
	curl -f http://localhost:8000/health || echo "$(RED)Backend недоступен$(NC)"
	curl -f http://localhost:3000 || echo "$(RED)Frontend недоступен$(NC)"

amo-auth: ## Авторизация в amoCRM
	@echo "$(GREEN)Открытие страницы авторизации amoCRM...$(NC)"
	open http://localhost:8000/api/auth/amo

amo-status: ## Проверить статус авторизации amoCRM
	@echo "$(GREEN)Статус авторизации amoCRM:$(NC)"
	curl -s http://localhost:8000/api/auth/amo/status | $(PYTHON) -m json.tool

amo-test: ## Тест подключения к amoCRM
	@echo "$(GREEN)Тест подключения к amoCRM:$(NC)"
	curl -s http://localhost:8000/api/auth/amo/test | $(PYTHON) -m json.tool

create-lead: ## Создать тестовый лид
	@echo "$(GREEN)Создание тестового лида...$(NC)"
	curl -X POST http://localhost:8000/api/leads/ \
		-H "Content-Type: application/json" \
		-d '{"name": "Тест Тестов", "phone": "+79001234567", "email": "test@example.com", "utm_source": "test"}'

get-leads: ## Получить список лидов
	@echo "$(GREEN)Список лидов:$(NC)"
	curl -s http://localhost:8000/api/leads/ | $(PYTHON) -m json.tool

shell: ## Открыть shell в контейнере backend
	@echo "$(GREEN)Открытие shell в backend контейнере...$(NC)"
	$(DOCKER_COMPOSE) exec backend bash

db-shell: ## Открыть shell в базе данных
	@echo "$(GREEN)Открытие shell в базе данных...$(NC)"
	$(DOCKER_COMPOSE) exec db psql -U asia -d asia_crm

backup: ## Создать резервную копию БД
	@echo "$(GREEN)Создание резервной копии БД...$(NC)"
	$(DOCKER_COMPOSE) exec db pg_dump -U asia asia_crm > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore: ## Восстановить БД из резервной копии
	@echo "$(RED)Восстановление БД из резервной копии...$(NC)"
	@read -p "Введите имя файла резервной копии: " file; \
	$(DOCKER_COMPOSE) exec -T db psql -U asia asia_crm < $$file

dev: ## Запуск в режиме разработки
	@echo "$(GREEN)Запуск в режиме разработки...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up -d

prod: ## Запуск в режиме продакшн
	@echo "$(GREEN)Запуск в режиме продакшн...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d

# Специальные команды для amoCRM
amo-setup: ## Настройка интеграции amoCRM
	@echo "$(GREEN)Настройка интеграции amoCRM...$(NC)"
	@echo "1. Создайте приложение в amoCRM"
	@echo "2. Настройте OAuth2 права"
	@echo "3. Создайте кастомные поля"
	@echo "4. Настройте webhooks"
	@echo "5. Заполните .env файл"
	@echo "6. Запустите: make amo-auth"

amo-docs: ## Открыть документацию amoCRM
	@echo "$(GREEN)Открытие документации amoCRM...$(NC)"
	open https://www.amocrm.ru/developers/content/oauth/step-by-step

# Команды для разработки
format: ## Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	cd backend && black .
	cd frontend && npm run format

lint: ## Проверить код
	@echo "$(GREEN)Проверка кода...$(NC)"
	cd backend && flake8 .
	cd frontend && npm run lint

# Команды для мониторинга
monitor: ## Мониторинг системы
	@echo "$(GREEN)Мониторинг системы:$(NC)"
	@echo "CPU и память:"
	docker stats --no-stream
	@echo ""
	@echo "Дисковое пространство:"
	df -h
	@echo ""
	@echo "Логи ошибок:"
	$(DOCKER_COMPOSE) logs --tail=50 backend | grep ERROR || echo "Ошибок не найдено"

# Команды для webhook сервера
webhook-test: ## Тестирование webhook сервера
	@echo "$(GREEN)Тестирование webhook сервера...$(NC)"
	$(PYTHON) scripts/test_webhook_server.py

webhook-health: ## Проверка здоровья webhook сервера
	@echo "$(GREEN)Проверка здоровья webhook сервера...$(NC)"
	curl -s http://localhost:8000/api/webhooks/amo/health | $(PYTHON) -m json.tool

webhook-status: ## Статус webhook сервера
	@echo "$(GREEN)Статус webhook сервера...$(NC)"
	curl -s http://localhost:8000/api/webhooks/amo/test | $(PYTHON) -m json.tool

webhook-logs: ## Логи webhook сервера
	@echo "$(GREEN)Логи webhook сервера:$(NC)"
	$(DOCKER_COMPOSE) logs -f backend | grep -i webhook

webhook-simulate: ## Симуляция webhook от amoCRM
	@echo "$(GREEN)Симуляция webhook от amoCRM...$(NC)"
	curl -X POST http://localhost:8000/api/webhooks/amo \
		-H "Content-Type: application/json" \
		-H "X-Client-UUID: test-uuid" \
		-H "X-Signature: test-signature" \
		-H "X-Account-ID: test-account" \
		-d '{"leads": {"add": [{"id": 99999, "name": "Тестовый лид", "status_id": 1}]}}' | $(PYTHON) -m json.tool

webhook-setup: ## Настройка webhook сервера
	@echo "$(GREEN)Настройка webhook сервера...$(NC)"
	@echo "1. Проверьте конфигурацию в .env файле"
	@echo "2. Настройте webhook в amoCRM"
	@echo "3. Создайте кастомные поля"
	@echo "4. Запустите: make webhook-test"
	@echo "5. Проверьте логи: make webhook-logs"

protect:
	bash ops/protect_branches.sh

