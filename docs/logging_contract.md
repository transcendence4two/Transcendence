# Logging Contract - HTTP (ECS / ELK)

This document defines the JSON logging contract for HTTP requests across the backend.
All services must follow this contract.

## Purpose

- ensure all logs are structured and indexable
- keep cross-service request correlation
- support dashboards, metrics, and alerts in ELK

## Contract Rules

1. Logs must be valid JSON objects.
2. Base ECS fields must be present on every log line.
3. Request/response events must use the field names below.
4. Do not emit plain-text application logs.

## Base Fields (Required)

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `@timestamp` | string | Yes | ISO 8601 UTC |
| `log.level` | string | Yes | `debug`, `info`, `warning`, `error`, `critical` |
| `message` | string | Yes | Event name/message |
| `service.name` | string | Yes | Service identifier |
| `service.environment` | string | Yes | `development`, `staging`, `production` |

## Request Context Fields

| Field | Type | Required | Source |
| --- | --- | --- | --- |
| `http.request.id` | string | Yes | request context middleware |
| `trace.id` | string | Yes | request context middleware |
| `http.request.method` | string | Yes | request context middleware |
| `url.path` | string | Yes | request context middleware |
| `url.route` | string | Yes | request context middleware |
| `client.address` | string/null | Yes | request context middleware |
| `user_agent.original` | string/null | Yes | request context middleware |

## Response/Outcome Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `http.response.status_code` | number | Yes (request completion events) | HTTP status |
| `event.duration` | number | Yes (request completion events) | nanoseconds |
| `event.outcome` | string | Yes (request completion events) | `success` or `failure` |
| `error.type` | string/null | Yes (request completion events) | exception class name |

## Optional Auth Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `user.id` | string | No | present when auth middleware is enabled |
| `user.roles` | array | No | present when auth middleware is enabled |

## Standard HTTP Events

| `message` value | Description |
| --- | --- |
| `request_received` | emitted when request enters the service |
| `request_completed` | emitted when request finishes (includes response fields) |
| `request_failed` | emitted on exception path |

All events for the same request must share `http.request.id` and `trace.id`.

## Middleware Registration Order

Register middlewares in this order:

1. `logging_middleware()`
2. `auth_middleware()` (optional)
3. `request_context_middleware()`

Why: in FastAPI/Starlette the last registered middleware runs first (outermost). This order keeps request context available for completion logs.

## Lifecycle Events

Services should also emit:

- `application_started`
- `application_stopped`

These events still need base fields (`@timestamp`, `log.level`, `service.name`, `service.environment`, `message`).

## Uvicorn Plain-Text Logs

To keep one JSON pipeline, disable Uvicorn text logs in logging config:

```python
"loggers": {
    "uvicorn.access": {"handlers": [], "propagate": False},
    "uvicorn.error": {"handlers": [], "propagate": False},
}
```

## Security

- never log secrets or tokens
- never log raw passwords
- avoid full request/response bodies unless explicitly scrubbed
