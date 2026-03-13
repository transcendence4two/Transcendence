# Log Retention Policy

This document describes the log retention policy for **Transcendence** services, using **Elasticsearch** with **ILM (Index Lifecycle Management)**. The goal is to ensure logs are available for analysis and troubleshooting without overloading storage.

---

## Context

**ILM (Index Lifecycle Management)** automatically manages the lifecycle of log indices. Each policy defines phases an index goes through:

- **Hot**: Active index receiving real-time data.
- **Warm**: Index no longer receives new data, optimized for search.
- **Cold**: Rarely accessed index, stored on cheaper media.
- **Delete**: Index removed from the cluster to free up space.

Retention times were chosen based on each service's criticality and log access frequency.

---

## Services and ILM Policies

| Service                        | ILM Policy             | Reason                                                                 |
|--------------------------------|----------------------|------------------------------------------------------------------------|
| `friends-service`               | `transcendence-short` | Friend activity logs are less critical. Short retention avoids unnecessary storage. |
| `managementuser-service`        | `transcendence-medium`| User management logs may be needed for auditing. Medium retention ensures enough history. |
| `tournament-service`            | `transcendence-long`  | Tournament logs are critical for historical analysis and disputes. Long retention required. |
| `emails-service`                | `transcendence-medium`| Email send/failure logs are useful for troubleshooting and auditing. |
| `game-service`                  | `transcendence-long`  | Game session logs are essential for bug analysis and player behavior tracking. |

---

## ILM Policy Details

### `transcendence-short`
- **Hot phase**: 7 days
- **Warm phase**: 14 days
- **Cold phase**: 30 days
- **Delete phase**: removed 30 days after entering cold

### `transcendence-medium`
- **Hot phase**: 14 days
- **Warm phase**: 30 days
- **Cold phase**: 60 days
- **Delete phase**: removed 60 days after entering cold

### `transcendence-long`
- **Hot phase**: 30 days
- **Warm phase**: 60 days
- **Cold phase**: 180 days
- **Delete phase**: removed 180 days after entering cold

---

## Notes

- Services with critical or auditable logs have longer retention.
- Services with low-criticality logs or fast growth have shorter retention to save storage.
- Policies may be adjusted based on cluster growth or team needs.

---

## References

- [Elasticsearch ILM Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-lifecycle-management.html)
- [Transcendence Logging Guidelines](docs/logging-guidelines.md)
