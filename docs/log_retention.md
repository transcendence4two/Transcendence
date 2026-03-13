# Log Retention Policy

This document describes the log retention policy for **Transcendence** services, using **Elasticsearch** with **ILM (Index Lifecycle Management)** and **SLM (Snapshot Lifecycle Management)**. The goal is to ensure logs are available for analysis and troubleshooting without overloading storage.

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

| Service | ILM Policy | Reason |
|--------|------------|--------|
| `friends-service` | `transcendence-short` | Friend activity logs are less critical. Short retention avoids unnecessary storage. |
| `managementuser-service` | `transcendence-medium` | User management logs may be needed for auditing. Medium retention ensures enough history. |
| `tournament-service` | `transcendence-long` | Tournament logs are critical for historical analysis and disputes. Long retention required. |
| `emails-service` | `transcendence-medium` | Email send/failure logs are useful for troubleshooting and auditing. |
| `game-service` | `transcendence-long` | Game session logs are essential for bug analysis and player behavior tracking. |

---

## ILM Policy Details

### transcendence-short

- **Hot phase**: 7 days
- **Warm phase**: 14 days
- **Cold phase**: 30 days
- **Delete phase**: removed 30 days after entering cold

### transcendence-medium

- **Hot phase**: 14 days
- **Warm phase**: 30 days
- **Cold phase**: 60 days
- **Delete phase**: removed 60 days after entering cold

### transcendence-long

- **Hot phase**: 30 days
- **Warm phase**: 60 days
- **Cold phase**: 180 days
- **Delete phase**: removed 180 days after entering cold

---

## Log Archiving Strategy

Because ILM eventually **deletes indices**, Transcendence also implements **log archiving** using **Snapshot Lifecycle Management (SLM)**.

SLM automatically creates **snapshots of log indices** before they are deleted. These snapshots act as backups and allow logs to be restored later if needed.

Snapshots are stored in a **local filesystem repository mounted in the Elasticsearch container**.

---

## Snapshot Repository

A local snapshot repository is configured in Elasticsearch:

```yaml
path.repo:
  - /snapshots
```

Snapshots created by SLM are stored in this location.

---

## Snapshot Lifecycle Policy

A snapshot policy periodically archives log indices from all services.

### Example Configuration

- **Schedule:** once per week
- **Repository:** `transcendence_local`

### Indices Included

- `friends-service-*`
- `managementuser-service-*`
- `tournament-service-*`
- `emails-service-*`
- `game-service-*`

Snapshots are automatically retained according to the policy configuration, and older snapshots are removed to avoid excessive storage usage.

---

## Log Recovery

If logs need to be investigated after their indices were deleted by **ILM**, they can be restored from snapshots.

### Recovery Process

1. Select the desired snapshot from the repository.
2. Restore the required index into the Elasticsearch cluster.
3. Query the restored logs normally through **Elasticsearch** or **Kibana**.

This mechanism ensures that historical logs remain recoverable even after ILM deletion.

---

## Notes

- Services with **critical or auditable logs** have longer retention.
- Services with **high log volume** use shorter retention policies to control storage usage.
- Snapshots provide a **safety layer**, allowing recovery of deleted indices.
- Snapshot storage is **local to the infrastructure**, but can be migrated to **cloud storage** in the future if required.

---

## References

- https://www.elastic.co/guide/en/elasticsearch/reference/current/index-lifecycle-management.html
- https://www.elastic.co/guide/en/elasticsearch/reference/current/snapshot-lifecycle-management.html
- `Transcendence Logging Guidelines (docs/logging-guidelines.md)
