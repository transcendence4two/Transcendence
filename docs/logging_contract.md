# 📜 Logging Contract — HTTP Requests (ELK)

This document defines the **structured logging contract (JSON)** for all HTTP requests
across the **Transcendence (42)** backend.

All services (`auth`, `game`, `chat`, `matchmaking`, etc.) **must comply** with this specification.

---

## 🎯 Purpose

Ensure that all logs:

- are **structured** (JSON)
- are **fully indexable** by the ELK stack
- allow **request, user and error tracing**
- enable **dashboards, alerts and metrics**

---

## 🧱 Log Model

Every HTTP request log is composed of **four logical blocks**:

> 🕒 Temporal  
> 🧭 Identity  
> 🌐 HTTP  
> 📦 Business

---

## 🕒 Temporal

Time-related metadata.

| Field         | Type   | Description                                      |
| ------------- | ------ | ------------------------------------------------ |
| `timestamp`   | string | Time when the log event was generated (ISO 8601) |
| `started_at`  | string | When request processing started                  |
| `finished_at` | string | When request processing finished                 |
| `duration_ms` | number | Total request duration in milliseconds           |

---

## 🧭 Identity

Correlation and traceability.

| Field        | Type        | Description                    |
| ------------ | ----------- | ------------------------------ |
| `request_id` | string      | Unique request identifier      |
| `trace_id`   | string      | Distributed tracing identifier |
| `user_id`    | string/null | Authenticated user ID          |
| `ip`         | string      | Client IP address              |
| `user_agent` | string      | Client User-Agent              |

---

## 🌐 HTTP

Technical request / response metadata.

| Field         | Type        | Description                                                         |
| ------------- | ----------- | ------------------------------------------------------------------- |
| `method`      | string      | HTTP method (`GET`, `POST`, etc.)                                   |
| `path`        | string      | Actual URL path (`/login`)                                          |
| `route`       | string      | Logical route (`/users/{id}`)                                       |
| `status_code` | number      | HTTP response code                                                  |
| `success`     | boolean     | `true` if `status_code < 400`                                       |
| `error_type`  | string/null | Error category (`auth_error`, `validation_error`, `db_error`, etc.) |
| `size_in`     | number      | Request payload size in bytes                                       |
| `size_out`    | number      | Response payload size in bytes                                      |

---

## 📦 Business

Domain-level context for **Transcendence**.

| Field           | Type        | Description                                |
| --------------- | ----------- | ------------------------------------------ |
| `service`       | string      | `auth`, `game`, `chat`, `matchmaking`      |
| `action`        | string      | `login`, `create_match`, `join_game`, etc. |
| `game_id`       | string/null | Game identifier                            |
| `tournament_id` | string/null | Tournament identifier                      |
| `env`           | string      | `dev`, `staging`, `prod`                   |

---

## 📌 Event

Each request log **must include**:

| Field   | Type   | Description                                                                  |
| ------- | ------ | ---------------------------------------------------------------------------- |
| `event` | string | Event name (`request_received`, `request_completed`, `request_failed`, etc.) |

---

## 📈 Standard Events

| `event`             | When it occurs                          |
| ------------------- | --------------------------------------- |
| `request_received`  | When the request enters the system      |
| `request_completed` | When the request finishes successfully  |
| `request_failed`    | When the request finishes with an error |

All events belonging to the same request **must share the same** `request_id`.

---

## 🔐 Security & Privacy

- Never log full request or response bodies by default
- Never log passwords, tokens, or sensitive data
- Prefer **structured fields** over free-text messages
- Logs **must** be emitted only as JSON

---

## 🔄 ELK Compatibility

Logs are emitted as **pure JSON**, enabling:

- `codec => json` in Logstash
- direct indexing in Elasticsearch
- dashboards in Kibana
- alerting and metrics
