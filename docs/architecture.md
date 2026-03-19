# Project Architecture

![Architecture](./architecture.png)

## Overview
A microservices project built with multiple languages and frameworks, orchestrated with Docker Compose.
The architecture follows an API-first pattern with clear separation of responsibilities between specialized services.

### Technology Stack
- **Backend**: Python, Elixir, Go
- **Frontend**: TypeScript/React com Vite
- **Infraestrutura**: Docker, Docker Compose, Nginx
- **Authentication**: JWT (Stateless)
- **Message Broker**: Redis (pub/sub e cache)
- **Database**: SQLite (dev), PostgreSQL (prod)
- **DevOps**: ELK Stack, Prometheus e Grafana

---

## Services

### 1. Usermanagement Service
**Language**: Python 3.13+
**Framework**: FastAPI  
**Port**: 8000 (internal), `/api/users/` (via Nginx HTTPS)

#### Responsibilities
- User management (CRUD)
- Authentication and authorization (JWT-based)
- Email validation
- Secure password hashing (bcrypt)

#### Dependency Stack
- **FastAPI**: Async web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: Database ORM
- **asyncpg**: Async PostgreSQL driver
- **aiosqlite**: Async SQLite driver
- **Redis**: Client for cache and events
- **Pydantic**: Data validation
- **passlib[bcrypt]**: Password hashing
- **email-validator**: Email validation

#### Internal Architecture (Clean Architecture)
```
src/
├── controller/          # Presentation layer (FastAPI routes)
│
├── core/               # Settings and utilities
│   ├── settings.py     # Environment variables
│   ├── exception_handlers.py  # Exception handling
│   └── utils.py        # Utility functions
├── domain/             # Business logic
│   ├── models/         # Domain models
│   ├── schemas/        # DTOs
│   └── services/       # Services
├── infrastructure/
│   └── event_publisher.py  # Event publishing
└── di_config.py        # Dependency injection
```

---

### 2. Emails Service
**Language**: Elixir 1.14+
**Framework**: Plug (Cowboy)
**Port**: 4001 (external)

#### Responsibilities
- Asynchronous email delivery
- Redis event subscriber (pub/sub)

#### Event-Driven Pattern
The emails service operates as an event subscriber:
1. User Management publishes an event to Redis when a user registers or changes their email
2. Emails Service listens to events on the Redis channel
3. Processes and sends the email

---

### 3. Friends Service
**Language**: Java 21+  
**Framework**: Quarkus (RESTEasy Reactive)  
**Port**: 8003 (internal), `/api/friends/` (via Nginx HTTPS)

#### Responsibilities
- Managing friendship links between users
- Sending, accepting, and rejecting friend requests
- Paginated listing of friends and pending requests
- Removing friendships (soft delete)

#### Internal Architecture (Hexagonal)
```
domain/          # Immutable models (records), repository interfaces, exceptions
application/     # Use cases (one per operation), output ports
infrastructure/  # REST resources, JPA repositories, REST client for usermanagement
```

#### Integration
- Calls usermanagement-service (`GET /internal/users/{id}/exists`) before creating requests
- Receives `X-User-Id` via header injected by Nginx after JWT validation
- Propagates `X-Request-ID` and `X-Trace-ID` on outgoing calls (log correlation)

---

### 4. Game Service
**Language**: Go  
**Protocol**: WebSocket 
**Port**: 8001

#### Responsibilities
- Core game logic
- Game room management
- Real-time communication via WebSocket
- Game state synchronization
- Event broadcasting to multiple clients

#### Characteristics
- Persistent WebSocket connections
- In-memory game state
- Synchronization with the tournament service for results

---

### 5. Tournament Service
**Language**: Python 3.13+  
**Framework**: FastAPI  
**Port**: 8002

#### Responsibilities
- Tournament management
- Matchmaking system
- Match result persistence
- Player rankings and statistics
- Tournament history

#### Integration
- Receives results from the Game Service via webhook (`POST /api/tournaments/webhooks/game-match-finished`)
- Calls the Game Service to create game sessions during matchmaking
- Maintains permanent match history (MatchRecord) and per-player statistics

---

## Infrastructure Layer

### Nginx (Reverse Proxy)
**Port**: 443 (HTTPS)

#### Role
- Single entry point for the frontend
- Request routing to backend services
- SSL/TLS

#### Routing
```
https://localhost:443/
├── /                        → Frontend (Static Files)
├── /api/users/              → Usermanagement Service:8000
├── /api/friends/            → Friends Service:8003
├── /api/tournaments/        → Tournament Service:8002
└── /api/health              → Usermanagement Service:8000
```

#### Authentication via auth_request
For protected routes, Nginx makes a sub-request to `GET /auth/validate` on the usermanagement-service before forwarding the request. If the JWT is valid, the usermanagement-service returns `200` with the `X-User-Id` header, which Nginx then injects into the original request.

#### Redis
1. **Cache**: Storage of frequently accessed data
2. **Message Broker**: Pub/Sub for inter-service communication
3. **Events**: Event stream for auditing and logs

#### Pub/Sub Topics
- `user:registered` - New user registered
- `user:updated` - User data changed
- `user:deleted` - User removed
- `game:finished` - Match finished
- `tournament:updated` - Tournament updated

---

## Frontend

**Technology**: React + TypeScript  
**Build**: Vite  
**Port**: 80 (internal), 443 (via Nginx)

#### Features
- JWT authentication stored in localStorage
- WebSocket for real-time game communication

#### Backend Integration
- REST API for user management
- WebSocket with Game Service for gameplay

---

## Data Flow

### User Lifecycle
```
1. Registration
   Frontend → Nginx → Usermanagement
   └─ Validates data
   └─ Creates user
   └─ Publishes "user:registered" event to Redis
   └─ Emails Service receives event
   └─ Sends welcome email

2. Login
   Frontend → Usermanagement
   └─ Validates credentials
   └─ Generates JWT
   └─ Returns token to client

3. Game
   Frontend → Game Service (WS)
   └─ Authenticated via JWT
   └─ Connected to game room
   └─ Broadcasting moves
   └─ Result sent to Tournament Service

4. Tournaments
   Game Service → Tournament Service
   └─ Saves result
   └─ Updates rankings
   └─ Publishes completion event
```

---

### Project Structure

```
Transcendence/
├── backend/
│   ├── emails-service/          # Email service (Elixir)
│   ├── friends-service/         # Friendship management (Java/Quarkus)
│   ├── game-service/            # Real-time game server (Go)
│   ├── tournament-service/      # Tournaments and matchmaking (Python)
│   └── usermanagement-service/  # User and authentication API (Python)
├── frontend/                    # React application (TypeScript/Vite)
├── infra/
│   ├── docker/                  # Dockerfiles and docker-compose.yml
│   ├── nginx/                   # Reverse proxy configuration
│   ├── elasticsearch/           # ILM, SLM and index configuration
│   ├── logstash/                # Log ingestion pipelines
│   ├── kibana/                  # Dashboards
│   ├── certs/                   # SSL certificates
│   └── scripts/                 # Bootstrap and setup
├── docs/
└── Makefile
```

---

## Observability

### Logging
- Structured logs in JSON
- ELK Stack for centralization
- Kibana for visualization

### Metrics
- Prometheus for collection
- Grafana for visualization
- `/metrics` endpoints on each service

---