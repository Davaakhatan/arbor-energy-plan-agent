.PHONY: help install dev build test lint clean docker-up docker-down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development
install: ## Install all dependencies
	cd backend && pip install -e ".[dev]"
	cd frontend && pnpm install

dev: ## Start development servers (requires Docker for DB/Redis)
	docker-compose up -d postgres redis
	@echo "Starting backend..."
	cd backend && uvicorn app.main:app --reload --port 8000 &
	@echo "Starting frontend..."
	cd frontend && pnpm dev

# Docker
docker-up: ## Start all services with Docker
	docker-compose up --build

docker-down: ## Stop all Docker services
	docker-compose down

docker-clean: ## Stop and remove all Docker volumes
	docker-compose down -v

# Backend
backend-install: ## Install backend dependencies
	cd backend && pip install -e ".[dev]"

backend-dev: ## Run backend development server
	cd backend && uvicorn app.main:app --reload --port 8000

backend-test: ## Run backend tests
	cd backend && pytest

backend-lint: ## Lint backend code
	cd backend && ruff check . && ruff format --check .

backend-format: ## Format backend code
	cd backend && ruff check --fix . && ruff format .

# Frontend
frontend-install: ## Install frontend dependencies
	cd frontend && pnpm install

frontend-dev: ## Run frontend development server
	cd frontend && pnpm dev

frontend-build: ## Build frontend for production
	cd frontend && pnpm build

frontend-lint: ## Lint frontend code
	cd frontend && pnpm lint

# Database
db-migrate: ## Run database migrations
	cd backend && alembic upgrade head

db-seed: ## Seed database with sample data
	cd backend && python -m app.db.seed

db-init: ## Initialize database (migrate + seed)
	$(MAKE) db-migrate
	$(MAKE) db-seed

db-reset: ## Reset database (CAUTION: destroys data)
	docker-compose down -v postgres
	docker-compose up -d postgres
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5
	$(MAKE) db-init

# Testing
test: ## Run all tests
	cd backend && pytest
	cd frontend && pnpm test || true

# Cleaning
clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
