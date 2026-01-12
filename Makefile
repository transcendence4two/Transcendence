DOCKER_COMPOSE = docker-compose -f infra/docker/docker-compose.yml

all: build
	@echo "Starting all services..."
	$(DOCKER_COMPOSE) up -d
	@echo "All services are starting. Use 'make logs' to see logs."

build:
	@echo "Building Docker images..."
	$(DOCKER_COMPOSE) build

down:
	@echo "Stopping all services..."
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

clean: down
	@echo "Removing volumes and cleaning up..."
	$(DOCKER_COMPOSE) down -v
	docker system prune -f

.PHONY:  all build down logs clean
