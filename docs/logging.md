# Logging Schema (ECS)

All backend services must emit logs as JSON using ECS-style fields.
This guarantees consistent parsing, filtering, and alerting in ELK.

## Required Base Fields

| Field | Type | Description |
| --- | --- | --- |
| `@timestamp` | string | ISO 8601 timestamp generated at log emit time |
| `log.level` | string | Severity level (`debug`, `info`, `warning`, `error`, `critical`) |
| `message` | string | Event/message name |
| `service.name` | string | Service identifier (for example `usermanagement-service`) |
| `service.environment` | string | Runtime environment (`development`, `staging`, `production`) |

## Request Correlation Fields

| Field | Type | Description |
| --- | --- | --- |
| `http.request.id` | string | Per-request identifier |
| `trace.id` | string | Trace identifier (defaults to request id if missing) |
| `http.request.method` | string | Request method |
| `url.path` | string | Raw request path |
| `url.route` | string | Resolved route template or fallback path |
| `client.address` | string/null | Client host/address |
| `user_agent.original` | string/null | Original User-Agent header |

## Response/Outcome Fields

| Field | Type | Description |
| --- | --- | --- |
| `http.response.status_code` | number | Response status |
| `event.duration` | number | Request duration in nanoseconds |
| `event.outcome` | string | `success` or `failure` |
| `error.type` | string/null | Exception type name when present |

## Optional Auth Fields

| Field | Type | Description |
| --- | --- | --- |
| `user.id` | string | Authenticated user id |
| `user.roles` | array | User roles from token |

## Example: request_received

```json
{
  "message": "request_received",
  "http.request.id": "6627dd39-b344-4230-b1bd-9c901b2874f0",
  "trace.id": "6627dd39-b344-4230-b1bd-9c901b2874f0",
  "http.request.method": "GET",
  "url.path": "/logging-test",
  "url.route": "/logging-test",
  "client.address": "127.0.0.1",
  "user_agent.original": "Mozilla/5.0 ...",
  "@timestamp": "2026-02-20T04:48:12.079006Z",
  "service.environment": "development",
  "service.name": "usermanagement-service",
  "log.level": "info"
}
```

## Example: request_completed

```json
{
  "message": "request_completed",
  "http.response.status_code": 200,
  "event.duration": 5581943,
  "event.outcome": "success",
  "error.type": null,
  "@timestamp": "2026-02-20T04:48:12.083656Z",
  "service.environment": "development",
  "service.name": "usermanagement-service",
  "log.level": "info"
}
```
