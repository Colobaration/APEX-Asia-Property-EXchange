.PHONY: help install test run build up down logs clean migrate superuser collectstatic

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	pip install -r requirements.txt

test: ## Запустить тесты
	python manage.py test tests -v 2

run: ## Запустить сервер разработки
	python manage.py runserver 8001

build: ## Собрать Docker образ админ-панели
	docker-compose -f ../docker-compose.staging.yml build admin-panel

up: ## Запустить админ-панель
	docker-compose -f ../docker-compose.staging.yml up -d admin-panel

down: ## Остановить админ-панель
	docker-compose -f ../docker-compose.staging.yml stop admin-panel

logs: ## Показать логи админ-панели
	docker-compose -f ../docker-compose.staging.yml logs -f admin-panel

clean: ## Очистить Docker ресурсы админ-панели
	docker-compose -f ../docker-compose.staging.yml down admin-panel
	docker volume rm apex-staging-network_admin_panel_logs apex-staging-network_admin_panel_media apex-staging-network_admin_panel_static 2>/dev/null || true

migrate: ## Применить миграции
	python manage.py migrate

superuser: ## Создать суперпользователя
	python manage.py createsuperuser

collectstatic: ## Собрать статические файлы
	python manage.py collectstatic --noinput

setup: ## Первоначальная настройка
	python manage.py migrate
	python manage.py collectstatic --noinput
	@echo "Настройка завершена!"

dev: ## Запустить в режиме разработки
	python manage.py runserver 8001

prod: ## Запустить в продакшн режиме
	docker-compose -f docker-compose.prod.yml up -d

backup: ## Создать резервную копию БД
	docker-compose exec postgres pg_dump -U apex_admin_user apex_admin_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore: ## Восстановить БД из резервной копии
	@read -p "Введите имя файла резервной копии: " file; \
	docker-compose exec -T postgres psql -U apex_admin_user apex_admin_db < $$file

shell: ## Открыть Django shell
	python manage.py shell

check: ## Проверить код
	python manage.py check
	flake8 .
	black --check .

format: ## Форматировать код
	black .
	isort .

lint: ## Проверить стиль кода
	flake8 .
	black --check .
	isort --check-only .

security: ## Проверить безопасность
	bandit -r .
	safety check

monitor: ## Мониторинг админ-панели
	@echo "=== Статус админ-панели ==="
	docker-compose -f ../docker-compose.staging.yml ps admin-panel
	@echo "\n=== Использование ресурсов ==="
	docker stats --no-stream asia-admin-panel-staging
	@echo "\n=== Логи последних ошибок ==="
	docker-compose -f ../docker-compose.staging.yml logs --tail=50 admin-panel | grep -i error || echo "Ошибок не найдено"

health: ## Проверить здоровье админ-панели
	@echo "Проверка админ-панели..."
	curl -f http://localhost:8002/admin/ || echo "Админ-панель недоступна"
	@echo "Проверка PostgreSQL..."
	docker-compose -f ../docker-compose.staging.yml exec db pg_isready -U asia -d asia_crm_staging || echo "PostgreSQL недоступен"
	@echo "Проверка Redis..."
	docker-compose -f ../docker-compose.staging.yml exec redis redis-cli ping || echo "Redis недоступен"

docs: ## Сгенерировать документацию
	@echo "Генерация документации..."
	# Здесь можно добавить команды для генерации документации

deploy: ## Деплой админ-панели
	@echo "Начинаем деплой админ-панели..."
	git pull origin main
	docker-compose -f ../docker-compose.staging.yml build admin-panel
	docker-compose -f ../docker-compose.staging.yml up -d admin-panel
	docker-compose -f ../docker-compose.staging.yml exec admin-panel python manage.py migrate
	docker-compose -f ../docker-compose.staging.yml exec admin-panel python manage.py collectstatic --noinput
	@echo "Деплой админ-панели завершен!"

rollback: ## Откат админ-панели
	@echo "Откат админ-панели к предыдущей версии..."
	git checkout HEAD~1
	docker-compose -f ../docker-compose.staging.yml build admin-panel
	docker-compose -f ../docker-compose.staging.yml up -d admin-panel
	@echo "Откат админ-панели завершен!"
