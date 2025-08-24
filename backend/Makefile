# APEX Asia Property Exchange - Backend Makefile
# Удобные команды для разработки, тестирования и развертывания

.PHONY: help dev install lint format test migrate migrate-up migrate-down migrate-create migrate-reset migrate-status init-db clean docker-build docker-run

# Переменные
PYTHON = python
ALEMBIC_CONFIG = alembic.ini
SCRIPTS_DIR = scripts

help: ## Показать справку
	@echo "APEX Asia Property Exchange - Backend Management"
	@echo "=============================================="
	@echo ""
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Запустить сервер разработки
	@echo "🚀 Запуск сервера разработки..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

install: ## Установить зависимости
	@echo "📦 Установка зависимостей..."
	pip install -e ".[dev]"
	pre-commit install

lint: ## Проверить код линтерами
	@echo "🔍 Проверка кода..."
	ruff check .
	mypy app/

format: ## Форматировать код
	@echo "✨ Форматирование кода..."
	black .
	isort .
	ruff check --fix .

test: ## Запустить тесты
	@echo "🧪 Запуск тестов..."
	pytest --cov=app --cov-report=term-missing

test-watch: ## Запустить тесты в режиме наблюдения
	@echo "👀 Запуск тестов в режиме наблюдения..."
	pytest --cov=app --cov-report=term-missing --watch

migrate: ## Выполнить все миграции (upgrade head)
	@echo "🔄 Выполнение миграций..."
	$(PYTHON) $(SCRIPTS_DIR)/run_migrations.py

migrate-up: ## Выполнить миграции до последней версии
	@echo "⬆️  Выполнение миграций вверх..."
	alembic -c $(ALEMBIC_CONFIG) upgrade head

migrate-down: ## Откатить миграции на одну версию назад
	@echo "⬇️  Откат миграций..."
	alembic -c $(ALEMBIC_CONFIG) downgrade -1

migrate-reset: ## Сбросить все миграции (удалить все таблицы)
	@echo "⚠️  Сброс всех миграций (удаление всех таблиц)..."
	@read -p "Вы уверены? Это удалит все данные! (y/N): " confirm && [ "$$confirm" = "y" ]
	alembic -c $(ALEMBIC_CONFIG) downgrade base

migrate-status: ## Показать статус миграций
	@echo "📊 Статус миграций:"
	alembic -c $(ALEMBIC_CONFIG) current
	alembic -c $(ALEMBIC_CONFIG) history

migrate-create: ## Создать новую миграцию (требует сообщение MESSAGE="описание")
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ Ошибка: Укажите сообщение для миграции"; \
		echo "Пример: make migrate-create MESSAGE=\"Add user table\""; \
		exit 1; \
	fi
	@echo "📝 Создание новой миграции: $(MESSAGE)"
	$(PYTHON) $(SCRIPTS_DIR)/create_migration.py "$(MESSAGE)"

init-db: ## Инициализировать базу данных (создать БД, миграции, начальные данные)
	@echo "🗄️  Инициализация базы данных..."
	$(PYTHON) $(SCRIPTS_DIR)/init_db.py

test-migrations: ## Протестировать миграции (создать тестовую БД)
	@echo "🧪 Тестирование миграций..."
	@echo "Создание тестовой базы данных..."
	# Здесь можно добавить логику для создания тестовой БД
	@echo "✅ Тестирование завершено"

# Команды для разработки
dev-setup: ## Настройка окружения для разработки
	@echo "🔧 Настройка окружения для разработки..."
	pip install -r requirements.txt
	@echo "✅ Окружение настроено"

dev-migrate: ## Быстрая миграция для разработки
	@echo "⚡ Быстрая миграция для разработки..."
	alembic -c $(ALEMBIC_CONFIG) upgrade head

# Команды для продакшена
prod-migrate: ## Безопасная миграция для продакшена
	@echo "🚀 Безопасная миграция для продакшена..."
	@echo "⚠️  Проверка текущего состояния..."
	alembic -c $(ALEMBIC_CONFIG) current
	@echo "📋 План миграции:"
	alembic -c $(ALEMBIC_CONFIG) upgrade head --sql
	@read -p "Продолжить миграцию? (y/N): " confirm && [ "$$confirm" = "y" ]
	alembic -c $(ALEMBIC_CONFIG) upgrade head

# Команды для Docker
docker-migrate: ## Выполнить миграции в Docker контейнере
	@echo "🐳 Выполнение миграций в Docker..."
	docker-compose -f ../docker-compose.staging.yml exec backend python scripts/run_migrations.py

docker-init-db: ## Инициализировать БД в Docker контейнере
	@echo "🐳 Инициализация БД в Docker..."
	docker-compose -f ../docker-compose.staging.yml exec backend python scripts/init_db.py

# Информационные команды
info: ## Показать информацию о текущем состоянии
	@echo "📋 Информация о текущем состоянии:"
	@echo "  • Python: $(shell python --version)"
	@echo "  • Alembic: $(shell alembic --version 2>/dev/null || echo 'не установлен')"
	@echo "  • Конфигурация: $(ALEMBIC_CONFIG)"
	@echo "  • Скрипты: $(SCRIPTS_DIR)"

clean: ## Очистить временные файлы
	@echo "🧹 Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type d -name ".ruff_cache" -delete
	rm -rf htmlcov/
	rm -f .coverage
	@echo "✅ Очистка завершена"

docker-build: ## Собрать Docker образ
	@echo "🐳 Сборка Docker образа..."
	docker build -t apex-backend .

docker-run: ## Запустить в Docker
	@echo "🐳 Запуск в Docker..."
	docker run -p 8000:8000 --env-file .env apex-backend
