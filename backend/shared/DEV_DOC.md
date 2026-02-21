# Shared Middlewares & Logging - Developer Guide

## Overview

This shared package standardizes **structured logging** and **middlewares** across backend microservices.  
**Goal**: consistent ECS-compatible JSON logs for ELK, with service-to-service correlation.

## Standardization Goals

Ensure all microservices:

- emit ECS-compatible JSON logs
- include startup/shutdown lifecycle logs
- do not mix plain-text Uvicorn logs with JSON application logs
- follow one reusable logging pattern

## Structure

```text
shared/
├── setup.py               # Package installation
└── shared/
    ├── __init__.py        # Exports public functions
    ├── logging/
    │   ├── config.py      # structlog configuration
    │   └── processors.py  # Custom processors
    └── middlewares/
        ├── request_context.py  # request context + timing
        ├── auth.py             # JWT authentication
        └── logging.py          # request completion logs
```

## How To Use In Your Service

### Configure in `main.py`

This is an **example template** based on `usermanagement-service`.  
Adapt imports, routers, and domain modules to your own service.

```python
import asyncio
import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from shared import (
    configure_logging,
    logging_middleware,
    request_context_middleware,
)

from src.controller import user as user_controller
from src.core.exception_handlers import (
    app_exception_handler,
    general_exception_handler,
)
from src.core.settings import settings
from src.di_config import engine
from src.domain.exceptions import DomainError
from src.domain.models import Base

configure_logging(service_name="usermanagement-service")

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    max_attempts = 15
    for attempt in range(1, max_attempts + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break
        except Exception:
            if attempt == max_attempts:
                raise
            await asyncio.sleep(1)

    logger.info("Usermanagement service started")

    yield

    logger.info("Usermanagement service terminated")
    logging.shutdown()

    await engine.dispose()


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

# Exceptions handler
app.add_exception_handler(DomainError, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.middleware("http")(logging_middleware())
# app.middleware("http")(auth_middleware())
app.middleware("http")(request_context_middleware())

# Routes
app.include_router(user_controller.router, prefix="/users", tags=["users"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

## Lifecycle Logging

Why log startup/shutdown:

- makes restarts visible during incidents
- confirms healthy boot after deploy
- improves ELK timeline correlation

Why `configure_logging()` must come first:

- guarantees JSON ECS formatting from the first log line
- prevents unstructured logs during startup

Why call `logging.shutdown()` on termination:

- flushes and closes logging handlers before process exit
- reduces risk of losing final log events during shutdown
- is especially important when using network/file handlers

Why to avoid `print()`:

- prints unstructured text to stdout
- breaks JSON parsing when mixed in ELK streams
- has no request/trace context

## What Each Middleware Does

1. **request_context_middleware**
- generates or reads `http.request.id`
- binds `http.request.id`, `trace.id`, `http.request.method`, `url.path`, `url.route`, `client.address`, `user_agent.original`
- adds `X-Request-ID` response header

2. **auth_middleware**
- validates JWT from `Authorization`
- binds `user.id`, `user.roles`
- stores auth data in `request.state`

3. **logging_middleware**
- calculates request duration
- binds `http.response.status_code`, `event.duration`, `event.outcome`, `error.type`
- emits final `request_completed` event

Execution order (request -> response):

- request: `request_context` -> `auth` -> `logging`
- response: `logging` -> `auth` -> `request_context`

## ECS Log Shape Example

```json
{
  "@timestamp": "2026-02-20T04:48:12.083656Z",
  "log.level": "info",
  "message": "request_completed",
  "service.name": "usermanagement-service",
  "service.environment": "development",
  "trace.id": "6627dd39-b344-4230-b1bd-9c901b2874f0",
  "http.request.method": "GET",
  "url.path": "/logging-test",
  "http.response.status_code": 200,
  "event.duration": 5581943,
  "event.outcome": "success"
}
```

Expected minimum ECS fields:

- `@timestamp`
- `log.level`
- `service.name`
- `service.environment`
- `trace.id`
- `http.request.method`
- `url.path`
- `http.response.status_code`
- `event.duration`

## Best Practices

**Do**

- always create loggers with `structlog.get_logger(...)`
- add useful domain context fields (for example `user_id`, `order_id`, `room_id`)
- use `logger.exception(...)` inside `except` blocks
- keep the documented middleware order
- include lifecycle logs (`application_started` / `application_stopped`)

**Do not**

- do not use `print()` for application logs
- do not log sensitive data (passwords, tokens, card numbers)
- do not emit context-free logs when context exists
- do not re-bind the same context in multiple layers unnecessarily

## Troubleshooting

- **Logs are not JSON**  
  Confirm `configure_logging()` is called before app creation and shared package is installed correctly.

- **`service.name` is wrong**  
  Check the value passed to `configure_logging("correct-service-name")`.

- **Missing `http.request.id` in some logs**  
  Validate middleware registration order: `request_context` must be registered last (outermost).

- **Duplicate logs**  
  Ensure `configure_logging()` is called once and avoid `--reload` in production.

- **Still seeing plain-text Uvicorn logs**  
  Confirm this exists in `shared/logging/config.py`:

```python
"loggers": {
    "uvicorn.access": {"handlers": [], "propagate": False},
    "uvicorn.error": {"handlers": [], "propagate": False},
}
```

## Local Testing

```bash
# Development
uvicorn main:app --reload

# Production-like run (no reload)
uvicorn main:app

# Test request
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/your-route

# Example logs
{"message": "application_started", "@timestamp": "...", "service.name": "..."}
{"message": "request_received", "http.request.id": "...", "trace.id": "..."}
{"message": "request_completed", "http.response.status_code": 200, "event.duration": 1234567}
{"message": "application_stopped", "@timestamp": "...", "service.name": "..."}
```

## Runtime Warning (Read This)

- **Use `--reload` only in development.**
- **In production, run without `--reload` to avoid extra processes and noisy logs.**

## ELK Usage

In Kibana you can:

- filter by `service.name: "usermanagement-service"`
- query by `http.request.id: "abc-123"` for full request journey
- create latency dashboards using `event.duration`
- create alerts using `log.level: "error"`

## Team Rationale

We standardize logging because observability in a microservices architecture depends on cross-service correlation.

ECS structured logs enable:

- efficient Elasticsearch queries
- reliable Kibana dashboards
- service-to-service tracing
- more accurate alerting

Mixing plain-text logs with JSON logs breaks parsing and makes production operations harder.
