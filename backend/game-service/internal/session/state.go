package session

import (
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/domain"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/protocol"
)

func (s *Session) broadcastState() {
	s.broadcast(s.ID, protocol.ServerMessage{
		Type:    protocol.TypeGameState,
		Payload: s.buildStatePayload(),
	})
}

func (s *Session) buildStatePayload() protocol.GameStatePayload {
	payload := protocol.GameStatePayload{
		Board: s.Board.ToStrings(),
		State: s.State.String(),
		Round: s.Round,
		Score: s.Score,
	}

	if s.lastRemoved != nil {
		payload.RemovedPiece = &protocol.PositionDTO{
			Row: s.lastRemoved.Row,
			Col: s.lastRemoved.Col,
		}
	}

	if s.State == domain.StatePlaying && s.Players[s.TurnIndex] != nil {
		currentPlayer := s.Players[s.TurnIndex]
		payload.CurrentTurn = currentPlayer.ID

		// Preview which piece will be removed on the current player's next move.
		history := s.MoveHistory[currentPlayer.Symbol]
		if len(history) >= domain.MaxPiecesPerPlayer {
			oldest := history[0]
			payload.NextRemovedPiece = &protocol.PositionDTO{
				Row: oldest.Row,
				Col: oldest.Col,
			}
		}
	}

	for _, p := range s.Players {
		if p != nil {
			payload.Players = append(payload.Players, protocol.PlayerInfo{
				ID:     p.ID,
				Symbol: string(p.Symbol),
			})
		}
	}

	for pid := range s.disconnectedPlayers {
		payload.DisconnectedPlayers = append(payload.DisconnectedPlayers, pid)
	}

	return payload
}
