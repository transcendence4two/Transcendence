package session

import (
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/transcendence4two/Transcendence/backend/game-service/internal/domain"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/protocol"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/tournament"
)

const DisconnectGracePeriod = 15 * time.Second

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

	Round int
	Score domain.MatchScore

	Config              *Config
	lastRemoved         *domain.Position
	broadcast           BroadcastFunc
	notify              NotifyFunc
	tournament          tournament.Client
	disconnectedPlayers map[string]*time.Timer
	roundResetTimer     *time.Timer
}

func NewSession(id string, broadcast BroadcastFunc, notify NotifyFunc, tc tournament.Client, cfg *Config) *Session {
	return &Session{
		ID:                  id,
		Board:               domain.NewBoard(),
		State:               domain.StateWaiting,
		TurnIndex:           0,
		MoveHistory:         domain.NewMoveHistory(),
		CreatedAt:           time.Now(),
		Round:               1,
		Config:              cfg,
		broadcast:           broadcast,
		notify:              notify,
		tournament:          tc,
		disconnectedPlayers: make(map[string]*time.Timer),
	}
}

func (s *Session) Join(playerID string) (*domain.Player, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if timer, ok := s.disconnectedPlayers[playerID]; ok {
		slog.Info("player reconnected", "session", s.ID, "player", playerID)
		if timer != nil {
			timer.Stop()
		}
		delete(s.disconnectedPlayers, playerID)

		s.broadcast(s.ID, protocol.ServerMessage{
			Type: protocol.TypePlayerJoined,
			Payload: protocol.PlayerJoinedPayload{
				PlayerID: playerID,
				Symbol:   string(s.getPlayerSymbol(playerID)),
			},
		})

		s.broadcastState()
		for _, p := range s.Players {
			if p != nil && p.ID == playerID {
				return p, nil
			}
		}
	}

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

	if s.Players[0] != nil && s.Players[1] != nil && s.State == domain.StateWaiting {
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

	if winner, line := domain.CheckWinner(s.Board); winner != domain.SymbolEmpty {
		s.broadcastState()
		s.finishRound(playerID, "checkmate", line)
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
			Reason:   "disconnect",
		},
	})

	if s.State != domain.StatePlaying {
		return
	}

	if existing, ok := s.disconnectedPlayers[playerID]; ok && existing != nil {
		existing.Stop()
	}

	timer := time.AfterFunc(DisconnectGracePeriod, func() {
		s.mu.Lock()
		defer s.mu.Unlock()

		if _, stillDisconnected := s.disconnectedPlayers[playerID]; !stillDisconnected || s.State != domain.StatePlaying {
			return
		}

		slog.Info("grace period expired, forfeiting",
			"session", s.ID, "player", playerID)

		var winnerID string
		for _, p := range s.Players {
			if p != nil && p.ID != playerID {
				winnerID = p.ID
			}
		}
		delete(s.disconnectedPlayers, playerID)
		s.finishMatch(winnerID, "forfeit", nil)
	})
	s.disconnectedPlayers[playerID] = timer

	slog.Info("grace period started",
		"session", s.ID, "player", playerID,
		"duration", DisconnectGracePeriod)
}

func (s *Session) IsFinished() bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.State == domain.StateFinished
}

func (s *Session) GetStatePayload() protocol.GameStatePayload {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.buildStatePayload()
}

func (s *Session) getPlayerSymbol(playerID string) domain.Symbol {
	for _, p := range s.Players {
		if p != nil && p.ID == playerID {
			return p.Symbol
		}
	}
	return domain.SymbolEmpty
}

func (s *Session) playerIndex(playerID string) int {
	for i, p := range s.Players {
		if p != nil && p.ID == playerID {
			return i
		}
	}
	return -1
}
