# APEX Asia Property Exchange - Main Makefile
# Управление всем проектом

.PHONY: help devloop test build deploy monitor backup clean

# Переменные
PROJECT_NAME = "APEX Asia Property Exchange"
ADMIN_PANEL_DIR = admin_panel
DOCKER_COMPOSE_FILE = docker-compose.staging.yml

help: ## Показать справку
	@echo "🚀 $(PROJECT_NAME) - Команды управления"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# DevLoop команды
devloop: ## Запустить devloop мониторинг
	@echo "🔄 Запуск DevLoop мониторинга..."
	@echo "📁 Отслеживаемые файлы:"
	@echo "   - admin_panel/**/*.py"
	@echo "   - admin_panel/**/*.html"
	@echo "   - docker-compose*.yml"
	@echo "   - *.md"
	@echo ""
	@echo "🔧 Автоматические действия:"
	@echo "   - Тестирование при изменении Python файлов"
	@echo "   - Проверка кода при изменении Python файлов"
	@echo "   - Миграции при изменении миграций"
	@echo "   - Сборка статических файлов при изменении статики"
	@echo "   - Сборка Docker при изменении Dockerfile"
	@echo ""
	@echo "📊 Проверки здоровья каждые 60 секунд"
	@echo "🔄 Нажмите Ctrl+C для остановки"
	@echo ""
	@while true; do \
		echo "🔄 Проверка изменений..."; \
		$(MAKE) devloop-check; \
		sleep 60; \
	done

devloop-check: ## Выполнить проверку devloop
	@echo "🔍 Проверка кода..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && python manage.py check
	@echo "🧪 Запуск тестов..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && python manage.py test tests -v 2
	@echo "🐳 Проверка Docker контейнеров..."
	@docker-compose -f $(DOCKER_COMPOSE_FILE) ps
	@echo "🌐 Проверка здоровья админ-панели..."
	@curl -f http://localhost:8002/admin/ > /dev/null 2>&1 && echo "✅ Админ-панель работает" || echo "❌ Админ-панель недоступна"

# Тестирование
test: ## Запустить все тесты
	@echo "🧪 Запуск тестов..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && python manage.py test tests -v 2

test-coverage: ## Запустить тесты с покрытием
	@echo "🧪 Запуск тестов с покрытием..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && coverage run --source='.' manage.py test tests -v 2 && coverage report

test-watch: ## Запустить тесты в режиме наблюдения
	@echo "👀 Запуск тестов в режиме наблюдения..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && python manage.py test tests -v 2 --keepdb

# Сборка
build: ## Собрать Docker образ
	@echo "🐳 Сборка Docker образа..."
	@docker-compose -f $(DOCKER_COMPOSE_FILE) build admin-panel

build-no-cache: ## Собрать Docker образ без кэша
	@echo "🐳 Сборка Docker образа без кэша..."
	@docker-compose -f $(DOCKER_COMPOSE_FILE) build --no-cache admin-panel

# Деплой
deploy: ## Деплой в staging
	@echo "🚀 Деплой в staging..."
	@docker-compose -f $(DOCKER_COMPOSE_FILE) up -d admin-panel
	@echo "✅ Деплой завершен"

deploy-production: ## Деплой в production
	@echo "🚀 Деплой в production..."
	@echo "⚠️  Внимание: Это production деплой!"
	@read -p "Продолжить? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "🚀 Выполняется production деплой..."

# Мониторинг
monitor: ## Мониторинг системы
	@echo "📊 Мониторинг системы..."
	@echo "=== Статус контейнеров ==="
	@docker-compose -f $(DOCKER_COMPOSE_FILE) ps
	@echo ""
	@echo "=== Использование ресурсов ==="
	@docker stats --no-stream asia-admin-panel-staging 2>/dev/null || echo "Контейнер не запущен"
	@echo ""
	@echo "=== Проверка здоровья ==="
	@curl -f http://localhost:8002/admin/ > /dev/null 2>&1 && echo "✅ Админ-панель работает" || echo "❌ Админ-панель недоступна"

monitor-logs: ## Просмотр логов
	@echo "📋 Просмотр логов..."
	@docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f admin-panel

# Резервное копирование
backup: ## Создать резервную копию
	@echo "💾 Создание резервной копии..."
	@mkdir -p backups
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec db pg_dump -U asia asia_crm_staging > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@tar -czf backups/files_$(shell date +%Y%m%d_%H%M%S).tar.gz $(ADMIN_PANEL_DIR)/
	@echo "✅ Резервная копия создана в папке backups/"

backup-restore: ## Восстановить из резервной копии
	@echo "🔄 Восстановление из резервной копии..."
	@echo "Доступные резервные копии:"
	@ls -la backups/ 2>/dev/null || echo "Папка backups/ пуста"
	@read -p "Введите имя файла для восстановления: " file; \
	if [ -f "backups/$$file" ]; then \
		echo "Восстанавливаем из $$file..."; \
		docker-compose -f $(DOCKER_COMPOSE_FILE) exec -T db psql -U asia asia_crm_staging < backups/$$file; \
		echo "✅ Восстановление завершено"; \
	else \
		echo "❌ Файл backups/$$file не найден"; \
	fi

# Очистка
clean: ## Очистить временные файлы
	@echo "🧹 Очистка временных файлов..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".DS_Store" -delete
	@echo "✅ Очистка завершена"

clean-docker: ## Очистить Docker ресурсы
	@echo "🐳 Очистка Docker ресурсов..."
	@docker system prune -f
	@docker volume prune -f
	@echo "✅ Docker очистка завершена"

clean-all: clean clean-docker ## Полная очистка

# Безопасность
security-scan: ## Сканирование безопасности
	@echo "🛡️ Сканирование безопасности..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && \
	bandit -r . -f json -o bandit-report.json && \
	safety check --json --output safety-report.json
	@echo "✅ Сканирование завершено"

# Разработка
dev: ## Запуск в режиме разработки
	@echo "🚀 Запуск в режиме разработки..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && python manage.py runserver 8002

dev-docker: ## Запуск в Docker режиме разработки
	@echo "🐳 Запуск в Docker режиме разработки..."
	@docker-compose -f $(DOCKER_COMPOSE_FILE) up -d admin-panel
	@echo "✅ Админ-панель запущена на http://localhost:8002/admin/"

# Миграции
migrate: ## Применить миграции
	@echo "🗄️ Применение миграций..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && python manage.py migrate

migrate-make: ## Создать миграции
	@echo "📝 Создание миграций..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && python manage.py makemigrations

# Статические файлы
collectstatic: ## Собрать статические файлы
	@echo "📦 Сборка статических файлов..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && python manage.py collectstatic --noinput

# Пользователи
createsuperuser: ## Создать суперпользователя
	@echo "👤 Создание суперпользователя..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && python manage.py createsuperuser

# Инициализация
init: ## Инициализация проекта
	@echo "🚀 Инициализация проекта..."
	@$(MAKE) migrate
	@$(MAKE) collectstatic
	@$(MAKE) createsuperuser
	@echo "✅ Инициализация завершена"

init-data: ## Инициализация тестовых данных
	@echo "📊 Инициализация тестовых данных..."
	@cd $(ADMIN_PANEL_DIR) && source venv/bin/activate && python manage.py shell -c "exec(open('scripts/init_data.py').read())"

# GitHub Actions
github-test: ## Запустить GitHub Actions тесты локально
	@echo "🔍 Запуск GitHub Actions тестов локально..."
	@act -j test

github-build: ## Запустить GitHub Actions сборку локально
	@echo "🏗️ Запуск GitHub Actions сборки локально..."
	@act -j build

# Отчеты
report: ## Создать отчет о состоянии
	@echo "📊 Создание отчета о состоянии..."
	@echo "=== Статус проекта ==="
	@echo "Проект: $(PROJECT_NAME)"
	@echo "Ветка: $$(git branch --show-current)"
	@echo "Коммит: $$(git rev-parse --short HEAD)"
	@echo ""
	@echo "=== Тесты ==="
	@$(MAKE) test > /dev/null 2>&1 && echo "✅ Тесты проходят" || echo "❌ Тесты не проходят"
	@echo ""
	@echo "=== Docker ==="
	@docker-compose -f $(DOCKER_COMPOSE_FILE) ps | grep admin-panel > /dev/null 2>&1 && echo "✅ Контейнер запущен" || echo "❌ Контейнер не запущен"
	@echo ""
	@echo "=== Здоровье ==="
	@curl -f http://localhost:8002/admin/ > /dev/null 2>&1 && echo "✅ Админ-панель доступна" || echo "❌ Админ-панель недоступна"

# Помощь
docs: ## Открыть документацию
	@echo "📚 Открытие документации..."
	@open admin_panel/README.md 2>/dev/null || echo "Файл README.md не найден"

logs: ## Просмотр логов
	@echo "📋 Просмотр логов..."
	@tail -f admin_panel/logs/django.log 2>/dev/null || echo "Файл логов не найден"

