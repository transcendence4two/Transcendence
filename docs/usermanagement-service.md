# Usermanagement Service — Technical Documentation

## Overview

The **usermanagement-service** is the platform's central identity service. It manages the user lifecycle, authentication (including 2FA and GitHub OAuth), avatar uploads, and online presence. It also acts as the **authentication gateway** for Nginx via `auth_request`.

---

## Service Architecture

```
main.py                               ← FastAPI entrypoint, router registration
src/
├── controller/
│   ├── user.py                       ← user, auth, OAuth, and presence routes
│   ├── auth.py                       ← GET /auth/validate (nginx auth_request)
│   └── internal.py                   ← GET /internal/users/{id}/exists (service-to-service)
├── core/
│   ├── settings.py                   ← environment variables (JWT, GitHub OAuth, Redis...)
│   ├── auth.py                       ← JWT extraction and validation from header
│   └── exception_handlers.py         ← exception → HTTP response mapping
├── domain/
│   ├── contracts.py                  ← abstract ports
│   ├── exceptions.py                 ← typed domain exceptions
│   ├── models/user.py                ← SQLAlchemy model (User)
│   ├── schemas/user.py               ← Pydantic DTOs (request/response)
│   └── services/
│       ├── user.py                   ← UserService (orchestration)
│       ├── token.py                  ← TokenService (JWT)
│       ├── password.py               ← PasswordService (bcrypt)
│       ├── otp.py                    ← OtpService (2FA code generation)
│       ├── presence.py               ← PresenceService (Redis TTL)
│       └── commands/                 ← one Command per write operation
│           ├── register_user.py
│           ├── login_user.py
│           ├── update_user_profile.py
│           ├── delete_user_profile.py
│           ├── github_oauth.py
│           ├── verify_two_factor.py
│           └── ...
└── infrastructure/
    ├── event_publisher.py            ← RedisEventPublisher (pub/sub)
    └── storage.py                    ← StorageService (MinIO)
```

---

## JWT Authentication Flow with Nginx

The service acts as an authentication provider for Nginx through the `auth_request` mechanism:

```
[Frontend]        [Nginx]          [usermanagement-service]     [destination service]
    │                │                        │                        │
    ├── GET /api/friends/ + JWT ──────────────►│                        │
    │             auth_request                │                        │
    │                ├── GET /auth/validate ──►│                        │
    │                │    Authorization: Bearer <jwt>                  │
    │                │◄── 200 OK               │                        │
    │                │    X-User-Id: "user_123"│                        │
    │                │                        │                        │
    │                ├── forwards request ──────────────────────────────►│
    │                │   + header X-User-Id: "user_123"                 │
```

**Authentication failure:** if the JWT is invalid or expired, the `/auth/validate` endpoint returns `401` and Nginx refuses the request without forwarding it to the destination service.

---

## Registration Flow and Welcome Email

```
[Frontend]                   [usermanagement-service]            [Redis]          [emails-service]
    │                                  │                            │                    │
    ├── POST /api/users/register ─────►│                            │                    │
    │   { username, email, password }  │                            │                    │
    │                                  │── validate uniqueness      │                    │
    │                                  │── bcrypt hash              │                    │
    │                                  │── persist User             │                    │
    │                                  │                            │                    │
    │                                  │── PUBLISH email:welcome ──►│                    │
    │                                  │   { email, username }      │── message ─────────►│
    │◄── 201 { UserResponse } ─────────│                           │                    │── sends email
```

---

## Login Flow with 2FA

```
[Frontend]                 [usermanagement-service]            [Redis]       [emails-service]
    │                               │                            │                 │
    ├── POST /api/users/login ─────►│                            │                 │
    │   { email, password }         │                            │                 │
    │                               │── authenticate credentials │                 │
    │                               │                            │                 │
    │   [2FA disabled]              │── generate final JWT       │                 │
    │◄── 200 { token } ─────────────│                            │                 │
    │                               │                            │                 │
    │   [2FA enabled]               │── generate temporary token │                 │
    │                               │   (5 min, no access)       │                 │
    │                               │── PUBLISH email:otp ──────►│                 │
    │◄── 200 { requires_2fa: true,  │   { email, otp_code }      │── message ─────►│
    │     temp_token } ─────────────│                            │                 │── sends OTP
    │                               │                            │                 │
    ├── POST /api/users/verify-2fa─►│                          │                 │
    │   { token: temp_token,        │── validate OTP             │                 │
    │     otp_code }                │── generate final JWT       │                 │
    │◄── 200 { token } ─────────────│                            │                 │
```

---

## Online Presence (Redis TTL)

The service tracks online users using Redis keys with TTL:

- **Heartbeat**: the frontend must periodically call `POST /api/users/presence/heartbeat`. This renews the `presence:{user_id}` key with a 70-second TTL.
- **Offline**: `POST /api/users/presence/offline` removes the key immediately.
- **Query**: `GET /api/users/{user_id}/presence` returns `{ online: true/false }`.

A user is considered offline if no heartbeat is received for more than 70 seconds.

---

## API Endpoints

All endpoints are prefixed with `/api/users`.

### Authentication & OAuth

| Method | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/register` | Public | Registers a new user |
| `POST` | `/login` | Public | Login with email/password |
| `POST` | `/verify-2fa` | Temporary token | Validates OTP code and returns final JWT |
| `GET` | `/oauth/github/authorize` | Public | Returns the GitHub authorization URL |
| `POST` | `/oauth/github/callback` | Public | Exchanges OAuth code for JWT |

### User Profile

| Method | Route | Auth | Description |
|---|---|---|---|
| `GET` | `/` | JWT | Lists all profiles (paginated) |
| `GET` | `/{user_id}` | JWT | Fetches profile by ID |
| `PUT` | `/{user_id}` | JWT | Updates profile |
| `DELETE` | `/{user_id}` | JWT (own user) | Deletes account (requires confirmation text) |
| `POST` | `/me/avatar` | JWT | Avatar upload (stored in MinIO) |

### Presence

| Method | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/presence/heartbeat` | JWT | Marks user as online |
| `POST` | `/presence/offline` | JWT | Marks user as offline |
| `GET` | `/{user_id}/presence` | JWT | Queries presence status |

### Internal endpoints (not routed through Nginx)

| Method | Route | Consumer | Description |
|---|---|---|---|
| `GET` | `/auth/validate` | Nginx | Validates JWT and returns `X-User-Id` |
| `GET` | `/internal/users/{id}/exists` | friends-service | Checks user existence |

---

## Redis Events Published

| Channel | Triggered by | Payload | Consumer |
|---|---|---|---|
| `email:welcome` | New user registration | `{ email, username }` | emails-service |
| `email:otp` | Login with 2FA enabled | `{ email, otp_code }` | emails-service |

---

## MinIO Integration (Avatars)

When uploading an avatar (`POST /me/avatar`), the `StorageService`:
1. Generates a unique UUID filename
2. Uploads the file to the `avatars` bucket in MinIO
3. Returns the public URL in the format `${MINIO_PUBLIC_URL}/avatars/${filename}`
4. Updates `avatar_url` on the user record

See [docs/minio.md](minio.md) for MinIO configuration details.

---

## Dependencies

| Dependency | Purpose |
|---|---|
| **FastAPI** | Async web framework |
| **Uvicorn** | ASGI server |
| **SQLAlchemy (async)** | ORM + queries |
| **asyncpg** | Async PostgreSQL driver |
| **aiosqlite** | Async SQLite driver (dev) |
| **passlib[bcrypt]** | Password hashing |
| **PyJWT** | JWT generation and validation |
| **redis.asyncio** | Pub/sub and online presence |
| **minio** | MinIO client (avatar upload) |
| **httpx** | HTTP client (GitHub OAuth API) |
| **structlog** | Structured logging (ECS) |

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | Database URL (SQLite or PostgreSQL) |
| `JWT_SECRET_KEY` | Secret key for signing JWTs |
| `JWT_ALGORITHM` | JWT algorithm (e.g. `HS256`) |
| `JWT_EXPIRES_MINUTES` | Token expiration time |
| `REDIS_URL` | Redis connection URL |
| `MINIO_ENDPOINT` | Internal MinIO endpoint |
| `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` | MinIO credentials |
| `MINIO_PUBLIC_URL` | Public MinIO URL (for avatar links) |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` | GitHub OAuth App credentials |
| `GITHUB_OAUTH_REDIRECT_URI` | GitHub OAuth callback URI |
| `SERVICE_NAME` | Log identifier (`usermanagement-service`) |
| `ENVIRONMENT` | `development` / `production` |
