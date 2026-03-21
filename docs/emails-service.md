# Emails Service — Technical Documentation

## Overview

The **emails-service** is an Elixir/OTP server responsible for delivering transactional emails asynchronously. It operates exclusively as a **Redis subscriber** and exposes no write endpoints — email delivery is always triggered by events published by other services.

### Responsibilities
- Listen to Redis events on channels `email:welcome` and `email:otp`
- Process payloads and send the corresponding emails via SMTP
- Expose `GET /health` for availability checks

---

## Service Architecture

```
lib/emails_service/
├── application.ex        ← OTP Application: starts Supervisor with Cowboy + EventSubscriber
├── router.ex             ← Plug router (GET /health only)
├── event_subscriber.ex   ← GenServer: Redis subscriber (Redix.PubSub)
├── mailer.ex             ← Swoosh: renders and sends emails via SMTP
└── swoosh.ex             ← Swoosh adapter configuration
```

The service is supervised by a `Supervisor` with the `one_for_one` strategy:

```
EmailsService.Supervisor
├── Plug.Cowboy          ← HTTP server on port 4001
└── EmailsService.EventSubscriber  ← Redis subscriber GenServer
```

---

## Event Flow

```
[usermanagement-service]             [Redis]              [emails-service]
         │                                │                       │
         ├── PUBLISH email:welcome ──────►│                       │
         │   { "email": "...",            │                       │
         │     "username": "..." }        │                       │
         │                                │── message ───────────►│
         │                                │                       │── EventSubscriber
         │                                │                       │   process_welcome_event/1
         │                                │                       │── Mailer.send_welcome_email/1
         │                                │                       │   (SMTP)
         │                                │                       │
         ├── PUBLISH email:otp ──────────►│                       │
         │   { "email": "...",            │                       │
         │     "otp_code": "..." }        │                       │
         │                                │── message ───────────►│
         │                                │                       │── EventSubscriber
         │                                │                       │   process_otp_event/1
         │                                │                       │── Mailer.send_otp_email/2
         │                                │                       │   (SMTP)
```

### Redis Channels

| Channel | Published by | Payload | Email sent |
|---|---|---|---|
| `email:welcome` | usermanagement-service (registration) | `{ email, username }` | Welcome message to new user |
| `email:otp` | usermanagement-service (2FA login) | `{ email, otp_code }` | 2FA verification code |

---

## EventSubscriber (GenServer)

The `EventSubscriber` connects to Redis using `Redix.PubSub` at startup. When a message is received:

1. Decodes the JSON payload
2. Dispatches to the corresponding handler (`process_welcome_event` or `process_otp_event`)
3. Calls the `Mailer` to deliver the email

If the Redis connection fails at startup, the process stops (`{:stop, reason}`) and the OTP Supervisor is responsible for restarting it.

---

## HTTP API

The service exposes a single endpoint, used by Docker for health checks:

| Method | Route | Description |
|---|---|---|
| `GET` | `/health` | Returns `{ "status": "ok" }` with HTTP 200 |

---

## Dependencies

| Dependency | Purpose |
|---|---|
| **Plug + Cowboy** | Minimal HTTP server |
| **Redix** | Redis client (pub/sub) |
| **Swoosh** | Email delivery abstraction |
| **Jason** | JSON serialization/deserialization |

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `SMTP_HOST` | SMTP host | — |
| `SMTP_PORT` | SMTP port | — |
| `SMTP_USERNAME` | SMTP username | — |
| `SMTP_PASSWORD` | SMTP password | — |
| `FROM_EMAIL` | Sender address | — |
