# Tournament Service — Technical Documentation

## Overview

The **tournament-service** is a Python/FastAPI server responsible for managing tournaments, matchmaking, and match history. It orchestrates game session creation in the **game-service** and receives match results via webhook.

---

## Service Architecture

```
main.py                           ← entrypoint, FastAPI app, router registration
src/
├── controller/
│   └── tournament.py             ← FastAPI routes (all endpoints)
├── core/
│   ├── settings.py               ← environment variables
│   ├── exception_handlers.py     ← global exception handling
│   └── webhook_auth.py           ← webhook token validation (game-service)
├── domain/
│   ├── contracts.py              ← abstract ports (TournamentManager, GameServiceClient)
│   ├── exceptions.py             ← domain exceptions
│   ├── models/
│   │   └── tournament.py         ← SQLAlchemy models (Tournament, Match, Queue...)
│   ├── schemas/
│   │   └── tournament.py         ← Pydantic DTOs (request/response)
│   └── services/
│       ├── tournament.py         ← TournamentService (business logic implementation)
│       └── game_client.py        ← HTTPGameServiceClient
└── di_config.py                  ← dependency injection (DB session, services)
```

---

## Domain Models

### Tournament
| Field | Type | Description |
|---|---|---|
| `id` | string (UUID) | Unique identifier |
| `name` | string | Tournament name |
| `status` | enum | `draft` → `active` → `finished` |
| `created_by` | string | user_id of the creator |
| `champion_user_id` | string\|null | user_id of the champion (filled when finished) |

### TournamentParticipant
| Field | Type | Description |
|---|---|---|
| `id` | string (UUID) | Unique identifier |
| `tournament_id` | string | FK to tournaments |
| `user_id` | string | User identifier |
| `display_name` | string | Name shown during matches |
| `wins` / `losses` | int | Win/loss counters within the tournament |
| `total_points` | int | Points accumulated in the tournament |

### TournamentMatch
| Field | Type | Description |
|---|---|---|
| `round_number` | int | Round number (1 = first round) |
| `match_order` | int | Order within the round |
| `player_one/two_participant_id` | string | FK to participants |
| `winner_participant_id` | string\|null | Winner (null until finished) |
| `status` | enum | `pending` → `in_progress` → `finished` |

### MatchmakingQueueEntry
| Field | Type | Description |
|---|---|---|
| `user_id` | string | User in queue (unique for `queued` status) |
| `preferred_game_mode` | string | E.g. `pong_1v1` |
| `tournament_id` | string\|null | If present, matchmaking is tied to a tournament |
| `status` | enum | `queued` → `matched` \| `cancelled` \| `expired` |
| `game_session_id` | string\|null | Filled when a pair is found |

### MatchRecord
Permanent record of every completed match (casual or tournament).

| Field | Type | Description |
|---|---|---|
| `game_service_match_id` | string\|null | Session ID in the game-service |
| `tournament_id` | string\|null | null for casual matches |
| `game_mode` | string | Game mode |
| `status` | enum | `pending` / `in_progress` / `finished` / `cancelled` |
| `winner_user_id` | string\|null | user_id of the winner |
| `winning_reason` | string\|null | E.g. `"disconnect"`, `"score"` |
| `duration_seconds` | int\|null | Match duration |

### MatchPlayerSnapshot
Per-player performance snapshot for a given match.

| Field | Type | Description |
|---|---|---|
| `match_record_id` | string | FK to match_records |
| `user_id` | string | Player identifier |
| `score` | int | Final score |
| `is_winner` | bool | Whether the player won |
| `disconnect_count` | int | Number of disconnections during the match |
| `latency_average_ms` / `latency_max_ms` | int\|null | Latency metrics |

---

## Flow 1: Casual Matchmaking

```
[Frontend]                        [tournament-service]              [game-service]
    │                                      │                              │
    ├── POST /api/tournaments/join ───────►│                              │
    │   { user_id, display_name,           │                              │
    │     preferred_game_mode }            │                              │
    │                                      │── acquire db lock ───────────│
    │                                      │── expire stale entries       │
    │                                      │── cancel previous queue entry│
    │                                      │── insert QueueEntry (queued) │
    │                                      │                              │
    │                                      │── find compatible opponent   │
    │                                      │   (same game_mode, no pair)  │
    │                                      │                              │
    │   [no opponent]                      │                              │
    │◄── { status: "queued" } ─────────────│                              │
    │                                      │                              │
    │   [opponent found]                   │── POST /api/sessions ───────►│
    │                                      │   { players: [...] }         │
    │                                      │◄── { session_id } ───────────│
    │                                      │                              │
    │                                      │── update both: matched       │
    │                                      │  game_session_id = session_id│
    │◄── { status: "matched",              │                              │
    │     game_session_id } ───────────────│                              │
    │                                      │                              │
    ├── GET /api/tournaments/              │                              │
    │   matchmaking/status/{user_id} ─────►│  (polling until matched)    │
    │◄── { status, game_session_id } ──────│                              │
```

**Lock mechanism:** the matchmaking uses a transactional lock on the `matchmaking_transaction_locks` table to prevent race conditions when pairing players.

---

## Flow 2: Structured Tournament

```
[Organizer]                       [tournament-service]
    │                                      │
    ├── POST /api/tournaments ────────────►│  creates tournament (status: draft)
    │                                      │
    ├── POST /api/tournaments/             │
    │   {id}/participants/register ───────►│  registers participants
    │   (repeated for each player)         │
    │                                      │
    ├── POST /api/tournaments/{id}/start ─►│  generates bracket
    │                                      │  status → active
    │                                      │  creates TournamentMatch for round 1
    │◄── [list of matches] ────────────────│
    │                                      │
    ├── POST /api/tournaments/             │
    │   {id}/matches/{match_id}/result ───►│  registers match result
    │                                      │  updates wins/losses/points
    │                                      │  if round complete → generates next
    │                                      │  if final → status = finished
```

**Bracket generation:** when `/start` is called, the service sorts participants by `joined_at` and creates sequential pairs for round 1. The participant count must be a power of 2 (2, 4, 8, 16...). At the end of each round, the next round is automatically generated with the winners.

---

## Flow 3: Receiving Results via Webhook

The game-service sends match results to the tournament-service when a match ends:

```
[game-service]                    [tournament-service]
    │                                      │
    ├── POST /api/tournaments/             │
    │   webhooks/game-match-finished ─────►│  authenticates via webhook token
    │   { game_service_match_id,           │  creates MatchRecord
    │     game_mode, status,               │  creates MatchPlayerSnapshot (x2)
    │     winner_user_id, players: [...] } │  updates PlayerStats
    │◄── { match_record, players } ────────│
```

The webhook is authenticated via a shared-secret header (`WEBHOOK_SECRET_TOKEN` in `.env`). Requests with an invalid or missing token receive `401`.

---

## API Endpoints

All endpoints are prefixed with `/api/tournaments`.

### Tournaments

| Method | Route | Description |
|---|---|---|
| `POST` | `/` | Creates a tournament (`status: draft`) |
| `GET` | `/{tournament_id}` | Fetches a tournament by ID |
| `POST` | `/{tournament_id}/start` | Starts the tournament and generates the bracket |
| `POST` | `/{tournament_id}/participants/register` | Registers a participant |
| `GET` | `/{tournament_id}/participants` | Lists participants |
| `GET` | `/{tournament_id}/matches` | Lists tournament matches |
| `POST` | `/{tournament_id}/matches/{match_id}/result` | Registers a match result |

### Matchmaking

| Method | Route | Description |
|---|---|---|
| `POST` | `/join` | Joins the matchmaking queue |
| `GET` | `/matchmaking/status/{user_id}` | Polls queue status |
| `POST` | `/matchmaking/leave/{user_id}` | Leaves the queue |

### History & Stats

| Method | Route | Description |
|---|---|---|
| `GET` | `/stats/players/{user_id}` | Global player statistics |
| `GET` | `/stats/players/{user_id}/matches` | Player match history |
| `POST` | `/save` | Manually saves a MatchRecord |
| `POST` | `/webhooks/game-match-finished` | game-service webhook (authenticated) |

---

## Integration with game-service

The tournament-service calls the game-service via HTTP to create game sessions during matchmaking:

```
POST {GAME_SERVICE_URL}/api/sessions
{
  "tournament_id": "",
  "match_id": "",
  "players": [
    { "user_id": "player1_id", "participant_id": "" },
    { "user_id": "player2_id", "participant_id": "" }
  ]
}

Response: { "session_id": "abc123" }
```

The base URL is configured via `GAME_SERVICE_URL` in `.env`.

---

## Dependencies

| Dependency | Purpose |
|---|---|
| **FastAPI** | Async web framework |
| **Uvicorn** | ASGI server |
| **SQLAlchemy (async)** | ORM + queries |
| **asyncpg** | Async PostgreSQL driver |
| **aiosqlite** | Async SQLite driver (dev) |
| **Pydantic** | DTO validation |
| **httpx** | HTTP client for game-service |
| **structlog** | Structured logging (ECS) |

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | Database URL  |
| `GAME_SERVICE_URL` | Base URL of the game-service |
| `WEBHOOK_SECRET_TOKEN` | Shared secret with the game-service for webhook auth |
| `SERVICE_NAME` | Log identifier (`tournament-service`) |
| `ENVIRONMENT` | `development` / `production` |
