# Task #28 - Backend Matchmaking

## Objetivo
Implementar o fluxo de matchmaking e persistência de partidas no `tournament-service`, conforme escopo:
- `POST /tournaments/join`
- `POST /tournaments/save`

Também foi adicionado webhook seguro para integração assíncrona com o Game Service.

## Escopo Entregue

### Matchmaking
- Endpoint `POST /tournaments/join` para entrada na fila de matchmaking.
- Validação de duplicidade para evitar múltiplas entradas `queued` do mesmo jogador.
- Match básico por modo de jogo/torneio, com atualização de status para `matched` quando par encontrado.

### Persistência de Partida
- Endpoint `POST /tournaments/save` para salvar dados completos da partida.
- Persistência de:
  - registro da partida (`MatchRecord`)
  - snapshot por jogador (`MatchPlayerSnapshot`)
- Validações de integridade:
  - consistência de vencedor
  - datas da partida
  - estrutura mínima de jogadores

### Integração por Webhook (segura)
- Endpoint `POST /tournaments/webhooks/game-match-finished`.
- Header obrigatório: `X-Webhook-Token`.
- Token validado por `WEBHOOK_SHARED_SECRET`.
- Reutiliza a mesma lógica de persistência do endpoint `/save`.

### Atualização de Estatísticas
- Atualização de `PlayerStats` com base nos snapshots persistidos.
- Sincronização de `TournamentMatch` quando `tournament_match_id` é informado.

### Robustez de Concorrência e Banco
- O `tournament-service` agora aceita configuração de banco dedicada por `TOURNAMENT_DATABASE_URL`.
- Mantivemos fallback para `DATABASE_URL` por compatibilidade com o setup atual do repo.
- A fila de matchmaking agora possui índice único parcial para impedir duas entradas `queued` do mesmo jogador.
- A captura do oponente foi endurecida com atualização condicional.
- Quando o serviço roda com PostgreSQL, a busca de oponente usa `FOR UPDATE SKIP LOCKED`.

## Modelagem Adicionada
Arquivo: `backend/tournament-service/src/domain/models/tournament.py`

- `MatchmakingQueueEntry`
- `MatchRecord`
- `MatchPlayerSnapshot`
- Enums:
  - `MatchmakingQueueStatus`
  - `MatchRecordStatus`

## Endpoints
- `POST /tournaments/join`
- `POST /tournaments/save`
- `POST /tournaments/webhooks/game-match-finished`

## Commits da Task
1. `99f5095`
   - `feat(tournament-service): add matchmaking and match record domain structures`
2. `e0be867`
   - `feat(tournament-service): add matchmaking join and match save endpoints with persistence`
3. `d92288e`
   - `feat(tournament-service): add secured game webhook for match persistence`

## Testes
Comando:
```bash
cd backend/tournament-service
uv run pytest -q
```

Resultado local:
- `8 passed`

## Concurrency Check (10 requisições simultâneas)
- Problema reproduzido no fluxo antigo: ao gerar 10 chamadas simultâneas em `POST /tournaments/join`, o serviço retornava `500` com `DATABASE_ERROR`.
- Causa real identificada: `_find_matchmaking_opponent()` usava `scalar_one_or_none()` em uma consulta que pode retornar mais de um jogador elegível na fila.
- Sob concorrência, múltiplos jogadores `queued` eram válidos ao mesmo tempo, e o SQLAlchemy lançava exceção ao encontrar mais de um resultado.
- Ajuste aplicado:
  - a consulta passou a usar `LIMIT 1`
  - a leitura agora usa `scalars().first()` para selecionar apenas o jogador mais antigo elegível
  - a captura do oponente agora faz atualização condicional para evitar dupla captura
  - a fila agora é protegida por índice único parcial para entradas `queued`
- Validação:
  - testes automatizados continuam passando (`8 passed`)
  - teste concorrente executado diretamente no código atual da branch com 20 chamadas simultâneas deixou de gerar exceção
  - resultado observado: todas as 20 requisições concluíram com `queued` ou `matched`, sem `500`
- Observação operacional:
  - `docker-compose exec` usa a imagem já construída
  - para validar essa correção via container, é necessário rebuildar o `tournament-service` antes do teste

## Fora de Escopo
- Algoritmo avançado de matchmaking (MMR/ELO completo, janelas por latência, etc.).
- Estratégias distribuídas de lock/coordenação entre múltiplas instâncias.
