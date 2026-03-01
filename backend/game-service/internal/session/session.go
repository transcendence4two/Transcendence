package session

import (
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/transcendence4two/Transcendence/backend/game-service/internal/domain"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/protocol"
)

type BroadcastFunc func(sessionID string, msg protocol.ServerMessage)
type NotifyFunc func(playerID string, msg protocol.ServerMessage)

type Session struct {
	mu sync.Mutex

	ID          string
	Board       domain.Board
	State       domain.GameState
	Players     [2]*domain.Player
	TurnIndex   int
	MoveHistory domain.MoveHistory
	StartedAt   time.Time
	CreatedAt   time.Time

	lastRemoved *domain.Position
	broadcast   BroadcastFunc
	notify      NotifyFunc
}

func NewSession(id string, broadcast BroadcastFunc, notify NotifyFunc) *Session {
	return &Session{
		ID:          id,
		Board:       domain.NewBoard(),
		State:       domain.StateWaiting,
		TurnIndex:   0,
		MoveHistory: domain.NewMoveHistory(),
		CreatedAt:   time.Now(),
		broadcast:   broadcast,
		notify:      notify,
	}
}

func (s *Session) Join(playerID string) (*domain.Player, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	for _, p := range s.Players {
		if p != nil && p.ID == playerID {
			return nil, fmt.Errorf("player %s already in session", playerID)
		}
	}

	var player *domain.Player
	switch {
	case s.Players[0] == nil:
		player = &domain.Player{ID: playerID, Symbol: domain.SymbolX}
		s.Players[0] = player
		slog.Info("player joined as X", "session", s.ID, "player", playerID)
	case s.Players[1] == nil:
		player = &domain.Player{ID: playerID, Symbol: domain.SymbolO}
		s.Players[1] = player
		slog.Info("player joined as O", "session", s.ID, "player", playerID)
	default:
		return nil, fmt.Errorf("session %s is full", s.ID)
	}

	s.broadcast(s.ID, protocol.ServerMessage{
		Type: protocol.TypePlayerJoined,
		Payload: protocol.PlayerJoinedPayload{
			PlayerID: player.ID,
			Symbol:   string(player.Symbol),
		},
	})

	if s.Players[0] != nil && s.Players[1] != nil {
		s.State = domain.StatePlaying
		s.StartedAt = time.Now()
		slog.Info("game started", "session", s.ID)
		s.broadcastState()
	}

	return player, nil
}

func (s *Session) HandleMove(playerID string, row, col int) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.State != domain.StatePlaying {
		return domain.ErrGameNotActive
	}

	currentPlayer := s.Players[s.TurnIndex]
	if currentPlayer == nil || currentPlayer.ID != playerID {
		return domain.ErrNotYourTurn
	}

	move := domain.Move{PlayerID: playerID, Row: row, Col: col}
	if err := domain.ValidateMove(s.Board, move); err != nil {
		return err
	}

	var removed *domain.Position
	s.Board, s.MoveHistory, removed = domain.ApplyMoveInfinity(
		s.Board, row, col, currentPlayer.Symbol, s.MoveHistory,
	)
	s.lastRemoved = removed

	slog.Info("move applied", "session", s.ID, "player", playerID,
		"row", row, "col", col, "symbol", currentPlayer.Symbol,
		"removed", removed)

	if winner := domain.CheckWinner(s.Board); winner != domain.SymbolEmpty {
		s.finishGame(playerID, "checkmate")
		return nil
	}

	s.TurnIndex = 1 - s.TurnIndex
	s.broadcastState()

	return nil
}

func (s *Session) Disconnect(playerID string) {
	s.mu.Lock()
	defer s.mu.Unlock()

	slog.Info("player disconnected", "session", s.ID, "player", playerID)

	s.broadcast(s.ID, protocol.ServerMessage{
		Type: protocol.TypePlayerLeft,
		Payload: protocol.PlayerLeftPayload{
			PlayerID: playerID,
		},
	})

	if s.State == domain.StatePlaying {
		var winnerID string
		for _, p := range s.Players {
			if p != nil && p.ID != playerID {
				winnerID = p.ID
			}
		}
		s.finishGame(winnerID, "forfeit")
	}
}

func (s *Session) GetStatePayload() protocol.GameStatePayload {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.buildStatePayload()
}

// finishGame must be called with s.mu held.
func (s *Session) finishGame(winnerID, reason string) {
	s.State = domain.StateFinished

	var loserID string
	for _, p := range s.Players {
		if p != nil && p.ID != winnerID {
			loserID = p.ID
		}
	}

	slog.Info("game finished",
		"session", s.ID,
		"winner", winnerID,
		"reason", reason,
	)

	s.broadcast(s.ID, protocol.ServerMessage{
		Type: protocol.TypeGameOver,
		Payload: protocol.GameOverPayload{
			WinnerID: winnerID,
			Reason:   reason,
			Board:    s.boardToStrings(),
		},
	})

	// TODO: delegate result to Tournament Service
	_ = domain.GameResult{
		SessionID: s.ID,
		WinnerID:  winnerID,
		LoserID:   loserID,
		Reason:    reason,
		Board:     s.Board,
		StartedAt: s.StartedAt,
		EndedAt:   time.Now(),
	}
}

// broadcastState must be called with s.mu held.
func (s *Session) broadcastState() {
	s.broadcast(s.ID, protocol.ServerMessage{
		Type:    protocol.TypeGameState,
		Payload: s.buildStatePayload(),
	})
}

// buildStatePayload must be called with s.mu held.
func (s *Session) buildStatePayload() protocol.GameStatePayload {
	payload := protocol.GameStatePayload{
		Board: s.boardToStrings(),
		State: s.State.String(),
	}

	if s.lastRemoved != nil {
		payload.RemovedPiece = &protocol.PositionDTO{
			Row: s.lastRemoved.Row,
			Col: s.lastRemoved.Col,
		}
	}

	if s.State == domain.StatePlaying && s.Players[s.TurnIndex] != nil {
		payload.CurrentTurn = s.Players[s.TurnIndex].ID
	}

	for _, p := range s.Players {
		if p != nil {
			payload.Players = append(payload.Players, protocol.PlayerInfo{
				ID:     p.ID,
				Symbol: string(p.Symbol),
			})
		}
	}

	return payload
}

func (s *Session) boardToStrings() [3][3]string {
	var out [3][3]string
	for i := 0; i < domain.BoardSize; i++ {
		for j := 0; j < domain.BoardSize; j++ {
			out[i][j] = string(s.Board[i][j])
		}
	}
	return out
}
