# Friends Service — Technical Documentation

## Overview

The **friends-service** is a Java/Quarkus server responsible for managing friendship relationships between users. It implements hexagonal architecture (Ports & Adapters) and integrates with the **usermanagement-service** to validate user existence before creating any links.

### Responsibilities
- Sending and receiving friend requests
- Accepting and rejecting requests
- Paginated listing of friends and pending requests
- Removing friendships (soft delete — `active = false`)

---

## Service Architecture

The service follows hexagonal architecture, separating domain, application, and infrastructure:

```
src/main/java/.../friends/
├── domain/
│   ├── model/
│   │   ├── FriendRequest.java      ← immutable record with factory methods
│   │   ├── Friendship.java         ← immutable record with factory methods
│   │   ├── RequestStatus.java      ← enum: PENDING, ACCEPTED, REJECTED
│   │   └── Page.java               ← generic pagination model
│   ├── repository/
│   │   ├── IFriendshipRepository.java
│   │   └── IFriendRequestRepository.java
│   └── exception/                  ← typed domain exceptions
│
├── application/
│   ├── usecase/                    ← one use case per operation
│   │   ├── SendFriendRequestUseCase.java
│   │   ├── AcceptFriendRequestUseCase.java
│   │   ├── RejectFriendRequestUseCase.java
│   │   ├── ListFriendsUseCase.java
│   │   ├── ListPendingRequestsUseCase.java
│   │   └── RemoveFriendUseCase.java
│   ├── port/out/
│   │   └── UserManagementPort.java ← port for user validation
│   └── dto/
│       ├── SendRequestDTO.java
│       └── PaginatedResponse.java
│
└── infrastructure/
    ├── rest/
    │   ├── FriendsResource.java    ← endpoints GET /friends, DELETE /friends/user/{id}
    │   ├── RequestsResource.java   ← endpoints /friends/requests
    │   ├── filter/
    │   │   └── RequestContextFilter.java  ← logging MDC (request_id, trace_id, user.id)
    │   ├── util/
    │   │   └── UserContextHelper.java
    │   └── exception/
    │       ├── DomainExceptionHandler.java
    │       └── GlobalExceptionHandler.java
    ├── client/
    │   ├── IUserManagementClient.java     ← declarative Quarkus REST Client
    │   └── HeaderPropagationFactory.java  ← propagation of X-Request-ID, X-Trace-ID
    ├── adapter/out/
    │   └── UserManagementAdapter.java     ← implementation of UserManagementPort
    ├── persistence/
    │   ├── entity/
    │   ├── repository/             ← JPA repository implementations
    │   └── util/
    │       └── PaginationHelper.java
    └── logging/
        └── LogstashHandlerConfigurer.java ← log forwarding to Logstash (ELK)
```

---

## Domain Models

Models are **immutable Java records** with factory methods, ensuring business rules stay in the domain.

### FriendRequest

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique identifier |
| `requesterId` | string | user_id of the sender |
| `receiverId` | string | user_id of the recipient |
| `status` | RequestStatus | `PENDING` → `ACCEPTED` \| `REJECTED` |
| `createdAt` / `updatedAt` | LocalDateTime | Timestamps |

**State transitions:**
- `FriendRequest.create(requesterId, receiverId)` → creates with `PENDING`
- `request.accept()` → returns new record with `ACCEPTED`
- `request.reject()` → returns new record with `REJECTED`

### Friendship

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique identifier |
| `userId1` / `userId2` | string | IDs of both users (stored in lexicographic order) |
| `active` | boolean | `false` = friendship removed (soft delete) |
| `createdAt` / `updatedAt` | LocalDateTime | Timestamps |

**Note:** IDs are always stored in lexicographic order to ensure that the pair `(A, B)` and `(B, A)` map to the same record. This prevents duplicates regardless of which user initiates the lookup.

**State transitions:**
- `Friendship.create(u1, u2)` → `active = true`
- `friendship.deactivate()` → `active = false`
- `friendship.reactivate()` → `active = true` (re-friend)

---

## Friendship Flow

### Sending a request

```
[Frontend]                       [friends-service]              [usermanagement-service]
    │                                    │                               │
    ├── POST /friends/requests ─────────►│                               │
    │   Header: X-User-Id: "user_A"      │                               │
    │   Body: { receiverId: "user_B" }   │                               │
    │                                    │── GET /internal/users/        │
    │                                    │   user_B/exists ─────────────►│
    │                                    │◄── 200 OK ────────────────────│
    │                                    │                               │
    │                                    │── check existing friendship   │
    │                                    │── check pending request       │
    │                                    │── create FriendRequest        │
    │◄── 201 { FriendRequest } ──────────│                               │
```

**Validations in `SendFriendRequestUseCase`:**
1. `requesterId != receiverId` (cannot send a request to yourself)
2. `userManagementPort.userExists(receiverId)` → calls usermanagement-service
3. Active friendship already exists → `FriendshipAlreadyExistsException`
4. Pending request from A→B already exists → `FriendRequestAlreadyExistsException`
5. Pending request from B→A already exists → `FriendRequestAlreadyExistsException` (with a message suggesting to accept)

### Accepting a request

```
[Frontend]                       [friends-service]
    │                                    │
    ├── POST /friends/requests/          │
    │   {requestId}/accept ─────────────►│
    │   Header: X-User-Id: "user_B"      │
    │                                    │── fetch FriendRequest by ID
    │                                    │── verify receiverId == currentUser
    │                                    │── request.accept() → status ACCEPTED
    │                                    │── create Friendship (or reactivate existing)
    │◄── 200 { Friendship } ─────────────│
```

### Removing a friendship

Removes (deactivates) the friendship via soft delete. The `Friendship` record remains in the database with `active = false`, allowing future reactivation when a new request is accepted.

---

## Integration with usermanagement-service

The service calls the `usermanagement-service` to check user existence before creating a friend request.

**Declarative client (Quarkus REST Client):**
```
GET {USERMANAGEMENT_URL}/internal/users/{id}/exists
Response: 200 OK   → user exists
Response: 404      → user not found
```

The `HeaderPropagationFactory` automatically propagates the `X-Request-ID` and `X-Trace-ID` headers on outgoing calls, maintaining log correlation across services.

---

## API Endpoints

All endpoints are prefixed with `/api/friends` (via Nginx).

### Friendships

| Method | Route | Required Header | Description |
|---|---|---|---|
| `GET` | `/friends` | `X-User-Id` | Lists current user's friends (paginated) |
| `DELETE` | `/friends/user/{friendUserId}` | `X-User-Id` | Removes a friendship (soft delete) |

**Pagination query params:** `page` (default: `1`), `page_size` (default: `10`)

### Friend Requests

| Method | Route | Required Header | Description |
|---|---|---|---|
| `POST` | `/friends/requests` | `X-User-Id` | Sends a friend request |
| `GET` | `/friends/requests` | `X-User-Id` | Lists incoming pending requests (paginated) |
| `POST` | `/friends/requests/{requestId}/accept` | `X-User-Id` | Accepts a request |
| `POST` | `/friends/requests/{requestId}/reject` | `X-User-Id` | Rejects a request |

**Note:** `X-User-Id` is injected by Nginx after JWT validation in usermanagement-service. The service does not handle tokens directly.

---

## Authentication and User Context

The friends-service does not validate JWT. The authentication flow is:

```
[Frontend]  ──JWT──►  [Nginx]  ──auth_request──►  [usermanagement-service /auth/validate]
                         │
                         │── injects X-User-Id into header
                         │
                         └─────────────────────►  [friends-service]
```

The `UserContextHelper` extracts the `X-User-Id` from the header and returns `401` if it is missing.

---

## Dependencies

| Dependency | Purpose |
|---|---|
| **Quarkus** | Base framework (CDI, configuration, native build) |
| **RESTEasy Reactive** | JAX-RS HTTP endpoints |
| **Quarkus REST Client** | Declarative HTTP client for usermanagement-service |
| **Hibernate ORM Panache** | Simplified JPA persistence |
| **PostgreSQL** | Production database |
| **Logstash Logback Encoder** | Structured JSON logs for ELK |

---

## Environment Variables

| Variable | Description |
|---|---|
| `QUARKUS_DATASOURCE_JDBC_URL` | PostgreSQL database URL |
| `QUARKUS_DATASOURCE_USERNAME` / `PASSWORD` | Database credentials |
| `QUARKUS_REST_CLIENT_USERMANAGEMENT_CLIENT_URL` | Base URL of the usermanagement-service |
