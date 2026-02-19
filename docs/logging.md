## 🧾 Log Schema

All backend services **must** emit logs in **JSON format** using the following standardized fields.  
This guarantees consistency, traceability, and full compatibility with the ELK stack.

### 🔑 Required Fields

| Field         | Type    | Description                                              |
| ------------- | ------- | -------------------------------------------------------- |
| `timestamp`   | string  | ISO 8601 timestamp when the event occurred               |
| `level`       | string  | Log severity (`debug`, `info`, `warn`, `error`, `fatal`) |
| `service`     | string  | Name of the service that produced the log                |
| `event`       | string  | Short machine-readable event name                        |
| `message`     | string  | Human-readable description of the event                  |
| `request_id`  | string  | Correlation ID for tracing requests across services      |
| `user_id`     | string? | Authenticated user ID (nullable if unauthenticated)      |
| `ip`          | string  | Client IP address                                        |
| `method`      | string  | HTTP method (`GET`, `POST`, etc.)                        |
| `path`        | string  | Requested URL path                                       |
| `status_code` | number  | HTTP response status code                                |
| `latency_ms`  | number  | Request processing time in milliseconds                  |

---

### 📦 Example Log

```json
{
  "timestamp": "2026-02-18T02:14:32.421Z",
  "level": "info",
  "service": "auth-api",
  "event": "user.login",
  "message": "User logged in successfully",
  "request_id": "c9f3b92d-a21f-4e77-aef5-0d1f4c91b233",
  "user_id": "42",
  "ip": "187.22.91.5",
  "method": "POST",
  "path": "/api/login",
  "status_code": 200,
  "latency_ms": 87
}
```
