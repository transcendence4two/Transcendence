# Task #28 - Guia de Execução e Teste para Review

## Pré-requisitos por Sistema Operacional

### macOS
- Docker Desktop ou Colima + Docker CLI
- `make`
- `git`
- `mkcert`
- `uv`
- `curl`

Exemplo de instalação:
```bash
brew install make git mkcert uv
```

### Linux
- Docker Engine + Docker Compose plugin
- `make`
- `git`
- `mkcert`
- `uv`
- `curl`

Exemplo (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install -y make git curl
```

`mkcert`, Docker e `uv` podem variar por distribuição e devem ser instalados conforme o gerenciador de pacotes do sistema.

### Windows
- Recomendado: WSL2 + Ubuntu
- Docker Desktop com integração WSL
- `make`
- `git`
- `mkcert`
- `uv`
- `curl`

No Windows puro, o fluxo pode variar mais. Para evitar diferença de ambiente, a forma mais estável de review é:
- usar WSL2
- rodar os comandos dentro do shell Linux no WSL

## Observação sobre Certificados
- Para `https://localhost`, o projeto usa certificado local.
- Se necessário, gere certificados antes do `make deploy`:
```bash
make certs
```

## Preparação

### 1) Ir para a branch da PR
```bash
git checkout feature/28-backend-matchmaking
git pull
```

### 2) Subir o projeto
```bash
make deploy
```

Se a avaliadora estiver testando após atualizar a branch com código novo do `tournament-service`, prefira rebuild explícito:
```bash
docker-compose -f infra/docker/docker-compose.yml up -d --build tournament-service nginx
```

Se quiser isolar o banco do `tournament-service`, a branch também aceita:
- `TOURNAMENT_DATABASE_URL`

Isso permite usar um banco dedicado para esse serviço sem reaproveitar a `DATABASE_URL` genérica do monorepo.

### 3) Validar health checks
```bash
curl -k https://localhost/api/health
curl -k https://localhost/api/tournaments/health
```

Resultado esperado:
- `{"status":"healthy"}` para o backend

## Teste 1 - Entrar na fila de matchmaking

### Primeiro player entra
```bash
curl -k -X POST https://localhost/api/tournaments/join \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "player_1",
    "display_name": "Player One",
    "preferred_game_mode": "pong_1v1"
  }'
```

### Segundo player entra
```bash
curl -k -X POST https://localhost/api/tournaments/join \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "player_2",
    "display_name": "Player Two",
    "preferred_game_mode": "pong_1v1"
  }'
```

Resultado esperado:
- primeiro player retorna `queued`
- segundo player pode retornar `matched`

### Testar duplicidade
```bash
curl -k -X POST https://localhost/api/tournaments/join \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "player_1",
    "display_name": "Player One",
    "preferred_game_mode": "pong_1v1"
  }'
```

Resultado esperado:
- status `409`
- `error_type: MATCHMAKING_QUEUE_ERROR`

## Teste 2 - Salvar uma partida manualmente

```bash
curl -k -X POST https://localhost/api/tournaments/save \
  -H "Content-Type: application/json" \
  -d '{
    "game_service_match_id": "game-service-match-001",
    "game_room_id": "room-001",
    "game_mode": "pong_1v1",
    "status": "finished",
    "winner_user_id": "player_1",
    "winning_reason": "score",
    "started_at": "2026-02-27T10:00:00+00:00",
    "ended_at": "2026-02-27T10:03:30+00:00",
    "duration_seconds": 210,
    "players": [
      {
        "user_id": "player_1",
        "display_name": "Player One",
        "player_side": "left",
        "score": 7,
        "is_winner": true
      },
      {
        "user_id": "player_2",
        "display_name": "Player Two",
        "player_side": "right",
        "score": 4,
        "is_winner": false
      }
    ]
  }'
```

Resultado esperado:
- status `201`
- retorno com `match_record`
- retorno com lista `players` contendo 2 snapshots

## Teste 3 - Ver estatísticas do jogador

```bash
curl -k https://localhost/api/tournaments/stats/players/player_1
```

Resultado esperado:
- `matches_played >= 1`
- `wins >= 1`

## Teste 4 - Webhook sem token

```bash
curl -k -X POST https://localhost/api/tournaments/webhooks/game-match-finished \
  -H "Content-Type: application/json" \
  -d '{
    "game_mode": "pong_1v1",
    "players": [
      {
        "user_id": "player_3",
        "display_name": "Player Three",
        "score": 3,
        "is_winner": false
      },
      {
        "user_id": "player_4",
        "display_name": "Player Four",
        "score": 7,
        "is_winner": true
      }
    ]
  }'
```

Resultado esperado:
- status `401`

## Teste 5 - Webhook com token válido

Se o `.env` estiver no valor padrão local:
- `WEBHOOK_SHARED_SECRET=local-webhook-token`

```bash
curl -k -X POST https://localhost/api/tournaments/webhooks/game-match-finished \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Token: local-webhook-token" \
  -d '{
    "game_service_match_id": "webhook-match-001",
    "game_mode": "pong_1v1",
    "status": "finished",
    "winner_user_id": "player_4",
    "winning_reason": "score",
    "players": [
      {
        "user_id": "player_3",
        "display_name": "Player Three",
        "score": 3,
        "is_winner": false
      },
      {
        "user_id": "player_4",
        "display_name": "Player Four",
        "score": 7,
        "is_winner": true
      }
    ]
  }'
```

Resultado esperado:
- status `201`
- partida salva com sucesso

## Teste Automatizado

```bash
cd backend/tournament-service
uv sync --extra test
uv run pytest -q
```

Resultado esperado:
- `8 passed`

## O que a avaliadora deve confirmar

1. Os endpoints pedidos pela task existem (`/join` e `/save`).
2. A fila impede duplicidade de jogador.
3. A partida persiste snapshots completos dos jogadores.
4. As estatísticas do jogador são atualizadas.
5. O webhook exige token válido.
6. O histórico está rastreável por commits atômicos.

## Nota de Concorrência
- Houve reprodução de erro com 10 requisições simultâneas no fluxo antigo de matchmaking.
- A causa era a busca de oponente assumir um único resultado possível, quando a fila podia conter vários candidatos válidos ao mesmo tempo.
- A correção limita a busca ao primeiro candidato elegível, faz captura condicional do oponente e protege a fila com índice único parcial.
- A branch também está preparada para usar `FOR UPDATE SKIP LOCKED` quando o banco configurado for PostgreSQL.
- Para validar esse ponto via Docker, é obrigatório rebuildar o container do `tournament-service` antes do teste, senão o `exec` continuará usando a imagem anterior.
