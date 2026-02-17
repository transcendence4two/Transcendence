DOCKER_COMPOSE = docker-compose -f infra/docker/docker-compose.yml

frontend:
	@echo "Starting frontend service locally..."
	cd frontend && bun run dev

infra-up:
	@echo "Starting infrastructure services..."
	$(DOCKER_COMPOSE) up -d redis

all: infra-up
	@echo "Starting backend service locally..."
	cd backend/usermanagement-service && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

deps:
	@echo "Installing dependencies with UV..."
	cd backend/usermanagement-service && uv sync

certs:
	@echo "Generating SSL certificates..."
	@chmod +x infra/scripts/generate-certs.sh
	@./infra/scripts/generate-certs.sh

certs-clean:
	@echo "Removing existing certificates..."
	@rm -rf infra/certs
	@echo "Certificates removed. Run 'make certs' to regenerate."

deploy: certs
	@echo "Deploying all Docker images..."
	$(DOCKER_COMPOSE) up --build -d

down:
	@echo "Stopping all services..."
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

tests:
	@echo "Running tests for usermanagement-service..."
	cd backend/usermanagement-service && uv sync --extra test && uv run pytest

lint:
	@echo "Linting code with Ruff..."
	cd backend/usermanagement-service && uv run ruff check .

format:
	@echo "Formatting code with Ruff..."
	cd backend/usermanagement-service && uv run ruff format .

clean: down
	@echo "Removing volumes and cleaning up..."
	$(DOCKER_COMPOSE) down -v
	docker system prune -f

.PHONY: deps all certs certs-clean deploy down logs tests lint format clean
