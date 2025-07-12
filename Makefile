.PHONY: help install install-dev setup-dev test test-unit test-integration test-e2e lint format clean run setup-db migrate deploy backup

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

setup-dev: ## Setup development environment (install deps, create .env, setup db)
	python scripts/setup_dev.py

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest tests/unit/

test-integration: ## Run integration tests only
	pytest tests/integration/

test-e2e: ## Run end-to-end tests only
	pytest tests/e2e/

test-cov: ## Run tests with coverage report
	pytest --cov=app --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	flake8 app/ tests/
	mypy app/

format: ## Format code with black
	black app/ tests/ scripts/

format-check: ## Check if code is formatted correctly
	black --check app/ tests/ scripts/

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

run: ## Run the development server
	python run.py

run-prod: ## Run the production server
	gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

setup-db: ## Setup the database
	python scripts/database/setup_database.py

migrate: ## Run database migrations
	python scripts/migrations/update_models.py

docker-build: ## Build Docker image
	docker build -t proper .

docker-run: ## Run Docker container
	docker run -p 5000:5000 proper

docker-compose-up: ## Start services with Docker Compose
	docker-compose up -d

docker-compose-down: ## Stop Docker Compose services
	docker-compose down

deploy: ## Deploy to production server
	chmod +x scripts/deploy.sh
	./scripts/deploy.sh

backup: ## Create database backup
	chmod +x scripts/backup_db.sh
	./scripts/backup_db.sh

check: format-check lint test ## Run all checks (format, lint, test)

pre-commit: clean install-dev check ## Prepare for commit 