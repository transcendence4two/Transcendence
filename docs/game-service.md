# Game Service — Documentação Técnica

## Visão Geral

O **game-service** é um servidor Go que gerencia partidas de Tic Tac Infinity em tempo real via WebSocket. Ele é consumido pelo frontend React e se integra com o **tournament-service** para registrar resultados de partidas.

### Variante "Infinity"
Cada jogador pode ter no máximo **3 peças** no tabuleiro. Quando coloca a 4ª peça, a mais antiga é automaticamente removida (FIFO). Isso faz com que o jogo nunca empate.

---

## Arquitetura do Serviço

```
cmd/server/main.go          ← entrypoint, HTTP server, graceful shutdown
internal/
├── config/config.go        ← variáveis de ambiente (SERVER_PORT, ALLOWED_ORIGINS, etc.)
├── domain/
│   ├── game.go             ← tipos do domínio (Board, Player, Move, GameState)
│   └── engine.go           ← regras do jogo (ValidateMove, ApplyMoveInfinity, CheckWinner)
├── protocol/message.go     ← mensagens WebSocket (client→server e server→client)
├── session/
│   ├── config.go           ← SessionConfig (contexto de torneio opcional)
│   ├── session.go          ← lógica de uma partida (Join, HandleMove, Disconnect)
│   └── manager.go          ← gerencia múltiplas sessões + limpeza automática
├── tournament/client.go    ← HTTP client para reportar resultados ao tournament-service
└── transport/
    ├── client.go           ← leitura/escrita WebSocket por conexão
    ├── handler.go          ← rotas HTTP (/ws, /health, /api/sessions)
    └── hub.go              ← coordena conexões, broadcast por sessão
```

---

## Fluxo Completo: Matchmaking → Partida → Resultado

### 1. Matchmaking (tournament-service + frontend)

```
[Frontend]                            [tournament-service]                [game-service]
    │                                         │                                │
    ├── POST /api/tournaments/join ──────────►│                                │
    │   { user_id, display_name }             │                                │
    │                                         │── (encontra par) ─────────────►│
    │                                         │   POST /api/sessions           │
    │                                         │   { tournament_id, match_id,   │
    │                                         │     players: [...] }           │
    │                                         │◄── { session_id } ──────────── │
    │◄── { status: "matched",                 │                                │
    │     game_session_id }                   │                                │
```

O frontend faz polling em `GET /api/tournaments/matchmaking/status/{user_id}` até receber `status: "matched"` com o `game_session_id`. Então navega para `/game/{sessionId}`.

### 2. Conexão WebSocket e Join

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
    │◄── { type: "game_state",                      │  (broadcast atualizado
    │     payload: { board, current_turn,           │   com removed_piece e
    │       removed_piece, next_removed } } ────────│   next_removed_piece)
```

### 4. Fim de Jogo

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

Motivos de fim: `checkmate` (3 em linha) ou desconexão
---

## Pontos Importantes

### Reconexão com Grace Period
Se um jogador desconecta durante uma partida ativa, o servidor **não declara vitoria imediatamente**. Há uma janela de **15 segundos** para reconexão:
- O backend inicia um timer ao detectar desconexão
- Se o jogador reconecta (mesmo `player_id` faz `Join` novamente), o timer é cancelado e o jogo continua
- Se o timer expira, o oponente vence por forfeit

O frontend implementa *auto-reconnect*

### Broadcast por Sessão
O Hub mantém um índice `rooms: map[sessionID] → set[Client]`. Ao fazer broadcast, o servidor consulta apenas os clients daquela sessão em vez de varrer todos os clients conectados.

### Limpeza Automática de Sessões

O `Manager` roda um goroutine que a cada 1 minuto limpa:

| Tipo | TTL | Motivo |
|:---|:---|:---|
| Sessões finalizadas | 30 segundos | Permite que clientes leiam o resultado final |
| Sessões órfãs (waiting) | 5 minutos | Sessões criadas mas nunca preenchidas |
---