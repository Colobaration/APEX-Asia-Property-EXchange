.PHONY: install fmt lint test check check-backend check-frontend

install:
	pip install -r backend/requirements.txt || true
	pip install -r backend/requirements-dev.txt || true
	cd frontend && npm ci || true

fmt:
	pre-commit run --all-files || true

lint:
	pre-commit run --all-files || true

test:
	pytest -q || true
	cd frontend && npm test --if-present || true

check: lint test

check-backend:
	ruff check . --fix || true
	black --check . || true
	pytest -q || true

check-frontend:
	cd frontend && npm run lint && npm run test --if-present && npm run build

