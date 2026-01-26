DOCKER_COMPOSE = docker-compose -f infra/docker/docker-compose.yml

all: deps
	@echo "Starting all services locally..."
	cd backend/usermanagement-service && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

deps:
	@echo "Installing dependencies with UV..."
	cd backend/usermanagement-service && uv sync

deploy:
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

clean: down
	@echo "Removing volumes and cleaning up..."
	$(DOCKER_COMPOSE) down -v
	docker system prune -f

.PHONY: deps all deploy down logs tests clean
