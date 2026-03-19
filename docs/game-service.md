# Game Service — Technical Documentation

## Overview

The **game-service** is a Go server that manages real-time Tic Tac Infinity matches via WebSocket. It is consumed by the React frontend and integrates with the **tournament-service** to register match results.

### "Infinity" Variant
Each player can have at most **3 pieces** on the board. When placing the 4th piece, the oldest one is automatically removed (FIFO). This ensures the game never ends in a draw.

---

## Service Architecture

```
cmd/server/main.go          ← entrypoint, HTTP server, graceful shutdown
internal/
├── config/config.go        ← environment variables (SERVER_PORT, ALLOWED_ORIGINS, etc.)
├── domain/
│   ├── game.go             ← domain types (Board, Player, Move, GameState)
│   └── engine.go           ← game rules (ValidateMove, ApplyMoveInfinity, CheckWinner)
├── protocol/message.go     ← WebSocket messages (client→server and server→client)
├── session/
│   ├── config.go           ← SessionConfig (optional tournament context)
│   ├── session.go          ← match logic (Join, HandleMove, Disconnect)
│   └── manager.go          ← manages multiple sessions + automatic cleanup
├── tournament/client.go    ← HTTP client to report results to tournament-service
└── transport/
    ├── client.go           ← per-connection WebSocket read/write
    ├── handler.go          ← HTTP routes (/ws, /health, /api/sessions)
    └── hub.go              ← coordinates connections, per-session broadcast
```

---

## Complete Flow: Matchmaking → Match → Result

### 1. Matchmaking (tournament-service + frontend)

```
[Frontend]                            [tournament-service]                [game-service]
    │                                         │                                │
    ├── POST /api/tournaments/join ──────────►│                                │
    │   { user_id, display_name }             │                                │
    │                                         │───────────────────────────────►│
    │                                         │   POST /api/sessions           │
    │                                         │   { tournament_id, match_id,   │
    │                                         │     players: [...] }           │
    │                                         │◄── { session_id } ──────────── │
    │◄── { status: "matched",                 │                                │
    │     game_session_id }                   │                                │
```

The frontend polls `GET /api/tournaments/matchmaking/status/{user_id}` until it receives `status: "matched"` with the `game_session_id`. Then it navigates to `/game/{sessionId}`.

### 2. WebSocket Connection and Join

```
[Frontend]                                     [game-service]
    │                                               │
    ├── WebSocket /ws?session_id=xxx ──────────────►│  (upgrade HTTP → WS)
    │                                               │
    ├── { type: "join",                             │
    │     payload: { player_id: "..." } } ─────────►│  → Session.Join()
    │                                               │
    │◄── { type: "player_joined", ... } ─────────── │  (broadcast)
    │                                               │
    │   (segundo jogador conecta e faz join)        │
    │                                               │
    │◄── { type: "game_state",                      │  → state: "playing"
    │     payload: { board, current_turn,           │    (jogo inicia)
    │                players, state } } ────────────│
```

### 3. Gameplay

```
[Jogador da vez]                               [game-service]
    │                                               │
    ├── { type: "move",                             │
    │     payload: { row, col } } ─────────────────►│  → Session.HandleMove()
    │                                               │     - ValidateMove
    │                                               │     - ApplyMoveInfinity
    │                                               │     - CheckWinner
    │                                               │
    │◄── { type: "game_state",                      │  broadcast atualizado
    │     payload: { board, current_turn,           │   com removed_piece e
    │       removed_piece, next_removed } } ────────│   next_removed_piece
```

### 4. End of game

```
[game-service]                              [tournament-service]
    │                                               │
    │── broadcast game_over ───────►[clients]       │
    │   { winner_id, reason, winning_line }         │
    │                                               │
    │── POST /tournaments/webhooks/                 │
    │   game-match-finished ───────────────────────►│  (salva registro)
    │   { winner_user_id, players, ... }            │
```

End reasons: `checkmate` (3 in a row) or disconnection
---

## Key Points

### Reconnection with Grace Period
If a player disconnects during an active match, the server **does not immediately declare a winner**. There is a **15-second** window for reconnection:
- The backend starts a timer when a disconnection is detected
- If the player reconnects (same `player_id` calls `Join` again), the timer is cancelled and the game continues
- If the timer expires, the opponent wins by forfeit

The frontend implements *auto-reconnect*

### Per-Session Broadcast
The Hub maintains a `rooms: map[sessionID] → set[Client]` index. When broadcasting, the server looks up only the clients for that session instead of scanning all connected clients.

### Automatic Session Cleanup

The `Manager` runs a goroutine every 1 minute to clean up:

| Type | TTL | Reason |
|:---|:---|:---|
| Finished sessions | 30 seconds | Allows clients to read the final result |
| Orphan (waiting) sessions | 5 minutes | Sessions created but never filled |
---