# Transcendence
The final 42 project

## Team board
[Board](https://github.com/orgs/transcendence4two/projects/6/views/2)

## Requirements
- Docker & Docker Compose
- Make
- MkCert
- .env file in the project root

## Quick Start
### Running Locally (Dev)
```bash
make all
```

### Running with Docker (Prod)
```bash
make deploy
```

### Other Commands
```bash
make logs    # View container logs
make down    # Stop all services
make clean   # Remove volumes and cleanup
make tests   # Run tests locally (needs UV local requirements)
```

# Architecture
![Schema](./docs/architecture.png)

## Project Structure
- `backend/emails-service` - Email sender application made in Elixir
- `backend/usermanagement-service` - User management FastAPI service
- `backend/game-service` - Core game logic and ws handler
- `backend/tournament-service` - Matchmaking and tournament information persistence
- `infra/docker` - Docker configurations