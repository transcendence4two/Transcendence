_This project has been created as part of the 42 curriculum by [aldantas](https://profile-v3.intra.42.fr/users/aldantas), [dbessa](https://profile-v3.intra.42.fr/users/dbessa), [jveras](https://profile-v3.intra.42.fr/users/jveras), [lraggio](https://profile-v3.intra.42.fr/users/lraggio) e [marcribe](https://profile-v3.intra.42.fr/users/marcribe)_

# Description
## Tic Tac Infinity
This section have to clearly presents the project, its goal and brief overview.

# Instructions

## Prerequisites

The following tools must be installed before running the project:

| Tool | Purpose | Install |
|------|---------|---------|
| **Docker & Docker Compose** | Container runtime for all services | [docs.docker.com](https://docs.docker.com/get-docker/) |
| **Make** | Build automation | `brew install make` / `apt install make` |
| **MkCert** | Local SSL certificate generation | `brew install mkcert` / `apt install mkcert` |

After installing MkCert, install the local CA:
```bash
mkcert -install
```

## Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Fill in the required values in `.env`:

   | Variable | Description |
   |----------|-------------|
   | `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | PostgreSQL credentials |
   | `REDIS_URL` | Redis connection URL |
   | `JWT_SECRET` | Secret key for JWT signing |
   | `JWT_ALGORITHM` | JWT algorithm (e.g. `HS256`) |
   | `JWT_EXPIRES_MINUTES` | Token TTL in minutes |
   | `JWT_ISSUER` | JWT issuer identifier |
   | `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` / `SMTP_FROM_EMAIL` | Email (SMTP) credentials |
   | `ELASTIC_PASSWORD` | Elasticsearch password |
   | `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` | MinIO object storage credentials |
   | `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` | Grafana dashboard credentials |

3. Generate SSL certificates:
   ```bash
   make certs
   ```

## Running the Project

### Development (local)
```bash
make all
```

### Production (Docker)
```bash
make deploy
```

### Stopping & Cleanup
```bash
make down    # Stop all services
make clean   # Stop and remove all volumes (full reset)
```

### Other Useful Commands
```bash
make logs    # Stream container logs
make tests   # Run test suite (requires UV installed locally)
make lint    # Lint Python services
make format  # Format Python services
```

## Accessing the Application

Once running, services are available at:

| Service | URL |
|---------|-----|
| **Frontend** | https://localhost |
| **Grafana** | https://localhost/grafana |
| **Kibana** | https://localhost/kibana |
| **Prometheus** | https://localhost/prometheus |
| **MinIO Console** | http://localhost:9001 |

# Resources

## Documentation & References

### Frontend
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Vite Documentation](https://vitejs.dev/guide/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Bun Documentation](https://bun.sh/docs)

### Backend
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Go Documentation](https://go.dev/doc/)
- [Gorilla WebSocket](https://pkg.go.dev/github.com/gorilla/websocket)
- [Elixir Documentation](https://elixir-lang.org/docs.html)
- [Quarkus Documentation](https://quarkus.io/guides/)

### Infrastructure & DevOps
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/16/)
- [Redis Documentation](https://redis.io/docs/)

### Monitoring & Observability
- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Logstash Documentation](https://www.elastic.co/guide/en/logstash/current/index.html)
- [Kibana Documentation](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)

### Security
- [MkCert - Local HTTPS](https://github.com/FiloSottile/mkcert)
- [OAuth 2.0 with GitHub](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)
- [JSON Web Tokens (JWT)](https://jwt.io/introduction)

## AI Usage

AI tools were used during the development of this project as a productivity aid. Below is a summary of how and where they were applied:

| Task | AI Tool | Description |
|------|---------|-------------|
| **Code assistance** | Claude (Anthropic) | Used for debugging, code suggestions, and understanding framework-specific patterns across multiple languages (Python, Go, Elixir, Java, TypeScript) |
| **Frontend styling** | Claude Code | Assisted with CSS/Tailwind responsive layout fixes and component styling adjustments |
| **Documentation** | Claude Code | Helped draft and structure sections of this README |
| **Configuration** | Claude Code | Assisted with Docker Compose and Nginx configuration files |

All AI-generated code was reviewed, tested, and validated by team members before being merged. The team maintained full ownership and understanding of the codebase — AI was used as an accelerator, not a replacement for engineering decisions.

# Team Information
### aldantas
```
Roles
- Tech Lead
- Developer

Responsabilities
- Resp1
- Resp2
```

### dbessa
```
Roles
- Project Manager
- Developer

Responsabilities
- Resp1
- Resp2
```

### jveras
```
Role
- Developer

Responsabilities
- Resp1
- Resp2
```

### lraggio
```
Roles
- Product Owner
- Developer

Responsabilities
- Resp1
- Resp2
```

### marcribe
```
Role
- Developer

Responsabilities
- Resp1
- Resp2
```

# Project Management
We used GitHub Projects with a Kanban board to manage our workflow, incorporating key Scrum ceremonies such as sprint planning and review sessions.

At the start of the project, we outlined the majority of the tasks upfront and added new ones as needs arose. Task assignment was handled on demand — whenever a team member was available, they would pick up the next task without any rigid distribution process.

We held weekly meetings on Discord to align on next steps and priorities, while day-to-day communication happened through our WhatsApp group.

# Technical Stack

## Frontend
- **React 19** with **TypeScript** — component-based UI with type safety
- **Tailwind CSS** — utility-first CSS framework for rapid, consistent styling
- **React Router DOM** — client-side routing and navigation
- **Vite** — fast development server and optimized production builds
- **Bun** — high-performance JavaScript runtime and package manager

## Backend
- **Python FastAPI** — User Management and Tournament services. Chosen for its async support, automatic API documentation, and team familiarity
- **Go** — Game Service. Chosen for its efficient concurrency model and low-latency WebSocket handling via Gorilla WebSocket
- **Elixir** — Email Service. Chosen for its fault-tolerant, concurrent architecture ideal for message processing
- **Java Quarkus** — Friends Service. Chosen for its fast startup, low memory footprint, and mature ORM ecosystem (Hibernate Panache)

## Database
- **PostgreSQL 16** — primary relational database shared across services. Chosen for its reliability, strong SQL compliance, and excellent support for concurrent access across multiple microservices
- **Redis 7** — in-memory data store used for caching and session management. Chosen for its speed and simplicity in handling ephemeral data
- **Elasticsearch 9** — used for centralized log storage and indexing as part of the ELK stack
- **MinIO** — S3-compatible object storage for user-uploaded assets (avatars). Chosen as a self-hosted alternative to cloud storage

## Other Significant Libraries
- **SQLAlchemy** (Python) and **Hibernate ORM Panache** (Java) — ORM layers for database access
- **Gorilla WebSocket** (Go) — real-time game communication
- **Swoosh** (Elixir) — email delivery abstraction
- **PyJWT** + **Passlib/bcrypt** — JWT authentication and password hashing
- **Flyway** (Java) — database migration management
- **Pydantic** (Python) — request/response validation

## Infrastructure & Observability
- **Docker & Docker Compose** — containerization and orchestration of all services
- **Nginx** — reverse proxy, SSL termination, and static file serving
- **Prometheus** + **Grafana** — metrics collection and dashboard visualization
- **ELK Stack** (Elasticsearch, Logstash, Kibana) — centralized logging and log analysis

## Justification for Major Technical Choices
The microservices architecture allowed each service to be built with the language best suited for its domain: Go for real-time game performance, FastAPI for rapid API development, Elixir for resilient message handling, and Quarkus for a lightweight Java service. PostgreSQL was chosen as the single database engine to simplify infrastructure while still supporting all services reliably. Docker was essential to unify the multi-language stack into a consistent, reproducible deployment.

# Database Schema
![DataSchema](./docs/database_schema.png)

# Feature list
Complete list of implemented features.
Which team member(s) worked on each feature.
Brief description of each feature’s functionality.

# Modules

---

### Major: Use a framework for both the frontend and backend
> Use a frontend framework (React, Vue, Angular, Svelte, etc.). Use a backend framework (Express, NestJS, Django, Flask, Ruby on Rails, etc.). Full-stack frameworks (Next.js, Nuxt.js, SvelteKit) count as both if you use both their frontend and backend capabilities.

**Why?** To accelerate development using well-known, battle-tested frameworks with strong community support and documentation.

**How?** On the frontend we used React with TypeScript and Vite. On the backend, each microservice uses its own framework: Python FastAPI for usermanagement-service and tournament-service, Elixir with Plug/Cowboy for emails-service, and Java Quarkus for friends-service.

**Who?** Frontend: dbessa, jveras | Backend: aldantas, lraggio, marcribe | Integrations: whole team

---

### Major: Real-time features using WebSockets
> Real-time updates across clients. Handle connection/disconnection gracefully. Efficient message broadcasting.

**Why?** The game requires real-time bidirectional communication between players — HTTP polling would introduce unacceptable latency for a live multiplayer experience.

**How?** The Game Service (Go) uses Gorilla WebSocket with a Hub pattern: a central Hub maintains a map of active clients and game rooms. Each client runs two goroutines — a ReadPump for incoming messages and a WritePump for outgoing ones. Clients connect via `/ws?session_id=<ID>`, and the Hub broadcasts game state updates (board, turns, scores, game over) to all players in a session. Disconnections trigger a 15-second grace period before forfeit.

**Who?** aldantas

---

### Major: Public API with rate limiting and documentation
> Interact with the database with a secured API key, rate limiting, documentation, and at least 5 endpoints (GET, POST, PUT, DELETE).

**Why?** A well-structured API is the backbone of a microservices architecture — it provides a clean interface between the frontend and each backend service while ensuring security and stability through rate limiting.

**How?** Each service exposes RESTful endpoints: User Management (`/api/users/` — register, login, profile CRUD, avatar upload, presence), Tournament (`/api/tournaments/` — create, join, matchmaking, stats, match history), Friends (`/api/friends/` — requests, accept/reject, list, remove), and Game (`/api/sessions/` — create session, get active session). Authentication is handled via JWT tokens validated at the Nginx layer through an `auth_request` subrequest. Rate limiting is configured in Nginx: 10 req/s for general API, 50 req/s for health checks, and 10 concurrent connections per IP. API documentation is auto-generated via Swagger/OpenAPI at `/api/{service}/docs`.

**Who?** aldantas, dbessa

---

### Minor: Use an ORM for the database
> Use an ORM to abstract database operations.

**Why?** ORMs reduce boilerplate SQL, enforce consistent data models across services, and make migrations safer by keeping the schema in code.

**How?** Python services use SQLAlchemy with async sessions (AsyncEngine + AsyncSession) to define models like User, Tournament, MatchRecord, and PlayerStats. The Java Friends Service uses Hibernate ORM Panache with JPA annotations for FriendshipEntity and FriendRequestEntity, including domain mappers and pagination support.

**Who?** aldantas, jveras

---

### Major: Standard user management and authentication
> Users can update their profile information. Users can upload an avatar (with a default avatar if none provided). Users can add other users as friends and see their online status. Users have a profile page displaying their information.

**Why?** User identity and social features are essential for a multiplayer game — players need accounts to track their stats, find opponents, and build a friends list.

**How?** The usermanagement-service (FastAPI) handles registration, login (with bcrypt password hashing), and profile updates. Avatars are uploaded as multipart files and stored in MinIO (S3-compatible object storage), with a default avatar assigned on registration. Online status is tracked via Redis: the frontend sends periodic heartbeat requests (`POST /presence/heartbeat`) that update a TTL-based key, so presence is automatically cleared when a player goes offline. The friends-service (Java Quarkus) manages friend requests and friendships through a RESTful API. The frontend displays profile pages with user info, stats, match history, and friend lists.

**Who?** aldantas, dbessa

---

### Minor: Remote authentication with OAuth 2.0
> Implement remote authentication with OAuth 2.0 (Google, GitHub, 42, etc.).

**Why?** Simplifying sign-in reduces friction for new users and makes returning users' login faster, helping lower drop-off rates.

**How?** We integrated GitHub OAuth 2.0. An OAuth App was created on GitHub with the homepage and callback URLs configured. On the frontend, clicking "Sign in with GitHub" redirects to GitHub's authorization page. After the user grants access, GitHub redirects back with an authorization code. The backend exchanges this code for an access token, fetches the user's GitHub profile, and either creates a new account or links to an existing one.

**Who?** dbessa

---

### Minor: Two-Factor Authentication (2FA)
> Implement a complete 2FA system for the users.

**Why?** 2FA adds an extra layer of security to user accounts, protecting against unauthorized access even if a password is compromised.

**How?** We implemented email-based OTP (One-Time Password). When a user with 2FA enabled logs in, the backend generates a 6-digit code, stores it in Redis with a 5-minute TTL, and publishes it to a Redis channel. The Email Service (Elixir) subscribes to that channel and delivers the code via SMTP using the Swoosh library. The user enters the code on the frontend, which is verified against Redis. On success, a full access token is issued. A short-lived temporary JWT is used between the login and verification steps.

**Who?** aldantas

---

### Major: Web-based multiplayer game
> The game can be real-time multiplayer. Players must be able to play live matches. The game must have clear rules and win/loss conditions. The game can be 2D or 3D.

**Why?** Since the original Transcendence project revolved around building a game (Pong), and the new subject gives us the flexibility to choose, we decided to build a Tic Tac Toe variant with a twist — "Infinity Mode."

**How?** The game is a modified Tic Tac Toe on a 3x3 board. The twist: each player can have at most 3 pieces on the board at a time. When a player places a 4th piece, their oldest piece is automatically removed. Win condition remains standard — 3 in a row (horizontal, vertical, or diagonal), but the piece must still be on the board. The backend (Go) manages game state through a state machine (Waiting → Playing → Finished), supports multi-round matches where players alternate who goes first, and tracks scores. The frontend renders the board with animated piece removal and SVG overlays for winning lines.

**Who?** aldantas, dbessa, jveras, lraggio, marcribe

---

### Major: Remote players
> Enable two players on separate computers to play the same game in real-time. Handle network latency and disconnections gracefully. Provide a smooth user experience for remote gameplay. Implement reconnection logic.

**Why?** A multiplayer game is only meaningful if players can compete from different machines — this module makes the game truly online.

**How?** Players connect via WebSocket to the Game Service. Each game session holds two players and synchronizes state through the Hub. When a player disconnects, the server starts a 15-second grace period — if the player reconnects in time, the game resumes; otherwise, the opponent wins by forfeit. On the frontend, a `useGameSocket` hook manages connection state and implements exponential backoff reconnection (1s → 2s → 4s → 8s → 16s, up to 5 attempts). The server maintains keep-alive via WebSocket ping/pong every 54 seconds. The UI shows real-time feedback: "Connection lost. Reconnecting in Xs (attempt N/5)..." and notifies when the opponent disconnects or reconnects.

**Who?** aldantas

---

### Major: ELK Stack for log management
> Elasticsearch to store and index logs. Logstash to collect and transform logs. Kibana for visualization and dashboards. Implement log retention and archiving policies. Secure access to all components.

**Why?** Centralized logging is critical for debugging and monitoring a distributed microservices system — without it, tracking issues across five services would be impractical.

**How?** Elasticsearch stores and indexes all logs with security enabled (`xpack.security`). Logstash receives logs via Beats (port 5044) and TCP/JSON (port 5000), then routes them to Elasticsearch using dynamic index naming based on service name mappings. Index Lifecycle Management (ILM) policies handle log retention and rollover automatically. Snapshot Lifecycle Management (SLM) policies handle archiving. Kibana is exposed behind Nginx at `/kibana` with authentication. Each backend service uses structured logging (structlog for Python, slog for Go, Logger for Elixir) with shared middleware that injects context like request ID and user ID.

**Who?** jveras, lraggio

---

### Major: Monitoring with Prometheus and Grafana
> Set up Prometheus to collect metrics. Configure exporters and integrations. Create custom Grafana dashboards. Set up alerting rules. Secure access to Grafana.

**Why?** Monitoring provides visibility into system health and performance — essential for detecting issues before they impact users in a multi-service architecture.

**How?** Prometheus scrapes metrics every 15 seconds from four exporters: Node Exporter (CPU, memory, disk), Postgres Exporter (connections, queries), Redis Exporter (memory, commands, keys), and Blackbox Exporter (HTTP probing of service health endpoints). Blackbox probes check availability of the main app, API health, and individual service health endpoints. Prometheus retains 15 days of data. Grafana connects to Prometheus as a datasource and serves dashboards behind Nginx. Anonymous access is disabled — authentication is required via admin credentials.

**Who?** jveras, lraggio

---

### Major: Backend as microservices
> Design loosely-coupled services with clear interfaces. Use REST APIs or message queues for communication. Each service should have a single responsibility.

**Why?** Microservices allowed us to pick the best tool for each domain: Go's concurrency model for real-time game logic, FastAPI's speed for CRUD-heavy services, Elixir's fault tolerance for email delivery, and Quarkus for a lightweight Java service. Loose coupling also enabled parallel development across the team.

**How?** Each service lives in its own directory under `backend/` with its own language, dependencies, and Dockerfile. Services communicate via REST APIs through Nginx, which handles routing, auth validation, and rate limiting. The Email Service uses Redis pub/sub to decouple OTP generation (Python) from email delivery (Elixir). Each service has a single responsibility: usermanagement-service (auth, profiles, presence), tournament-service (matchmaking, tournaments, stats), game-service (game logic, WebSocket), friends-service (social graph), and emails-service (email delivery).

**Who?** aldantas, marcribe

---

### Minor: Support for additional browsers
> Full compatibility with at least 2 additional browsers. Test and fix all features in each browser. Document any browser-specific limitations. Consistent UI/UX across all supported browsers.

**Why?** An easy win — since we developed using Google Chrome, we only needed to verify compatibility with other Chromium-based browsers.

**How?** The application was developed and primarily tested on Google Chrome. We verified full compatibility with Microsoft Edge and Brave, both of which are Chromium-based and rendered the application identically without any adjustments needed.

**Who?** aldantas, dbessa, jveras, lraggio, marcribe

---

### Minor: Custom design system with reusable components
> Custom-made design system with reusable components, including a proper color palette, typography, and icons (minimum: 10 reusable components).

**Why?** Building reusable components speeds up frontend development, ensures visual consistency, and follows industry best practices for scalable UI architecture.

**How?** We built a design system using Tailwind CSS with custom utility classes defined in `index.css`. The color palette centers on cyan/blue gradients for primary actions and slate tones for backgrounds, with full dark/light mode support. Typography uses Space Grotesk and DM Sans font families. Reusable components include: Button (with primary/secondary/hero variants), Card, StatCard, StatGrid, PageNavbar, HamburgerMenu, game board cells, profile shells, and page layout containers. All components are responsive with mobile-first breakpoints (`sm:`, `md:`).

**Who?** dbessa, jveras

---

```
Points calculation
2 + 2 + 2 + 1 + 2 + 1 + 1 + 2 + 2 + 2 + 2 + 2 + 1 + 1 = 23
```

# Individual Contributions
Detailed breakdown of what each team member contributed.

Specific features, modules, or components implemented by each person.
Any challenges faced and how they were overcome.
