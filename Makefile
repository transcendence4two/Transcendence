DOCKER_COMPOSE = docker compose --env-file .env -f infra/docker/docker-compose.yml

frontend:
	@echo "Starting frontend service locally..."
	cd frontend && bun run dev

infra-up:
	@echo "Starting infrastructure services..."
	$(DOCKER_COMPOSE) up -d redis

all: infra-up slm
	@echo "Starting backend service locally..."
	cd backend/usermanagement-service && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

deps:
	@echo "Installing dependencies with UV..."
	cd backend/usermanagement-service && uv sync

certs:
	@echo "Generating SSL certificates (dev - localhost)..."
	@chmod +x infra/scripts/generate-certs.sh
	@./infra/scripts/generate-certs.sh

certs-prod:
	@echo "Generating Let's Encrypt certificate for transcendentes.space..."
	@echo "  Requires: CERTBOT_EMAIL=you@email.com make certs-prod"
	@chmod +x infra/scripts/generate-certs.sh
	@DOMAIN=transcendentes.space ./infra/scripts/generate-certs.sh

certs-clean:
	@echo "Removing existing certificates..."
	@rm -rf infra/certs
	@echo "Certificates removed. Run 'make certs' to regenerate."

deploy: certs
	@echo "Deploying all Docker images..."
	$(DOCKER_COMPOSE) up --build -d

deploy-prod:
	@echo "Deploying to production VPS..."
	@chmod +x infra/scripts/deploy.sh
	@bash infra/scripts/deploy.sh

slm:
	@echo "Starting to create SLM policies"
	@chmod +x infra/scripts/setup-snapshot-repository.sh
	@./infra/scripts/setup-snapshot-repository.sh
	@chmod +x infra/scripts/setup-slm-policy.sh
	@./infra/scripts/setup-slm-policy.sh

down:
	@echo "Stopping all services..."
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

tests:
	@echo "Running tests for usermanagement-service..."
	cd backend/usermanagement-service && uv sync --extra test && uv run pytest
	@echo "Running tests for tournament-service..."
	cd backend/tournament-service && uv sync --extra test && uv run pytest
	@echo "Running tests for game-service..."
	cd backend/game-service && go test ./... -v -race
	@echo "Running tests for friends-service..."
	cd backend/friends-service && ./mvnw test

lint:
	@echo "Linting code with Ruff..."
	cd backend/usermanagement-service && uv run ruff check .

format:
	@echo "Formatting code with Ruff..."
	cd backend/usermanagement-service && uv run ruff format .

clean: down
	@echo "Removing unused Docker resources (volumes are preserved)..."
	docker system prune -f

fclean: down
	@echo "WARNING: Removing ALL volumes (database, minio, elasticsearch data will be lost)..."
	$(DOCKER_COMPOSE) down -v
	docker system prune -f

.PHONY: deps all certs certs-prod certs-clean deploy deploy-prod down logs tests lint format clean fclean
