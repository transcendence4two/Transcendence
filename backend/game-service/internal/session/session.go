package session

import (
	"context"
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/transcendence4two/Transcendence/backend/game-service/internal/domain"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/protocol"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/tournament"
)

const (
	DisconnectGracePeriod = 15 * time.Second
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

	Config      *SessionConfig
	lastRemoved *domain.Position
	broadcast   BroadcastFunc
	notify      NotifyFunc
	tournament  tournament.Client
	disconnectedPlayer string
	disconnectTimer    *time.Timer
}

func NewSession(id string, broadcast BroadcastFunc, notify NotifyFunc, tc tournament.Client, cfg *SessionConfig) *Session {
	return &Session{
		ID:          id,
		Board:       domain.NewBoard(),
		State:       domain.StateWaiting,
		TurnIndex:   0,
		MoveHistory: domain.NewMoveHistory(),
		CreatedAt:   time.Now(),
		Config:      cfg,
		broadcast:   broadcast,
		notify:      notify,
		tournament:  tc,
	}
}

func (s *Session) Join(playerID string) (*domain.Player, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Handle reconnection: if a disconnected player rejoins, cancel the forfeit timer.
	if s.disconnectedPlayer == playerID {
		slog.Info("player reconnected", "session", s.ID, "player", playerID)
		if s.disconnectTimer != nil {
			s.disconnectTimer.Stop()
			s.disconnectTimer = nil
		}
		s.disconnectedPlayer = ""

		s.broadcast(s.ID, protocol.ServerMessage{
			Type: protocol.TypePlayerJoined,
			Payload: protocol.PlayerJoinedPayload{
				PlayerID: playerID,
				Symbol:   string(s.getPlayerSymbol(playerID)),
			},
		})

		s.broadcastState()
		// Return existing player info
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
		s.finishGame(playerID, "checkmate", line)
		return nil
	}

	s.TurnIndex = 1 - s.TurnIndex
	s.broadcastState()

	return nil
}

// Disconnect handles a player disconnecting. During an active game, instead of
// immediately forfeiting, a grace period is started to allow reconnection.
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
		// Start grace period instead of immediate forfeit
		s.disconnectedPlayer = playerID
		s.disconnectTimer = time.AfterFunc(DisconnectGracePeriod, func() {
			s.mu.Lock()
			defer s.mu.Unlock()

			// Only forfeit if the player is still disconnected
			if s.disconnectedPlayer != playerID || s.State != domain.StatePlaying {
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
			s.disconnectedPlayer = ""
			s.disconnectTimer = nil
			s.finishGame(winnerID, "forfeit", nil)
		})

		slog.Info("grace period started",
			"session", s.ID, "player", playerID,
			"duration", DisconnectGracePeriod)
	}
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

// finishGame must be called with s.mu held.
func (s *Session) finishGame(winnerID, reason string, line []domain.Position) {
	s.State = domain.StateFinished

	// Clean up any pending disconnect timer
	if s.disconnectTimer != nil {
		s.disconnectTimer.Stop()
		s.disconnectTimer = nil
	}
	s.disconnectedPlayer = ""

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

	var winningLine []protocol.PositionDTO
	for _, p := range line {
		winningLine = append(winningLine, protocol.PositionDTO{
			Row: p.Row,
			Col: p.Col,
		})
	}

	s.broadcast(s.ID, protocol.ServerMessage{
		Type: protocol.TypeGameOver,
		Payload: protocol.GameOverPayload{
			WinnerID:    winnerID,
			Reason:      reason,
			Board:       s.boardToStrings(),
			WinningLine: winningLine,
		},
	})

	s.reportToTournament(winnerID, loserID)
}

func (s *Session) reportToTournament(winnerID, loserID string) {
	if s.tournament == nil {
		return
	}

	if s.Config == nil || (s.Config.TournamentID == "" && s.Config.MatchID == "") {
		s.saveMatchRecordViaWebhook(winnerID, loserID)
		return
	}

	winnerParticipant, ok := s.Config.ParticipantMap[winnerID]
	if !ok {
		slog.Warn("winner not found in participant map", "winner", winnerID)
		return
	}

	winnerScore, loserScore := 1, 0

	// Determine player order to match tournament's player_one/player_two
	p1Score, p2Score := winnerScore, loserScore
	if s.Players[1] != nil && s.Players[1].ID == winnerID {
		p1Score, p2Score = loserScore, winnerScore
	}

	payload := tournament.MatchResultPayload{
		WinnerParticipantID: winnerParticipant,
		PlayerOneScore:      p1Score,
		PlayerTwoScore:      p2Score,
	}

	go func() {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		if err := s.tournament.ReportResult(ctx, s.Config.TournamentID, s.Config.MatchID, payload); err != nil {
			slog.Error("failed to report result to tournament",
				"session", s.ID,
				"error", err,
			)
		}
	}()
}

func (s *Session) saveMatchRecordViaWebhook(winnerID, loserID string) {
	now := time.Now().UTC()
	duration := int(now.Sub(s.StartedAt).Seconds())
	startedAt := s.StartedAt.UTC()

	var players []tournament.MatchPlayerSnapshot

	for i, p := range s.Players {
		if p == nil {
			continue
		}
		side := "X"
		if i == 1 {
			side = "O"
		}
		score := 0
		isWinner := false
		if p.ID == winnerID {
			score = 1
			isWinner = true
		}
		players = append(players, tournament.MatchPlayerSnapshot{
			UserID:      p.ID,
			DisplayName: p.ID, // user_id as fallback display name
			PlayerSide:  side,
			Score:       score,
			IsWinner:    isWinner,
		})
	}

	payload := tournament.MatchRecordPayload{
		GameServiceMatchID: s.ID,
		GameMode:           "tic_tac_toe",
		Status:             "finished",
		WinnerUserID:       winnerID,
		WinningReason:      "checkmate",
		StartedAt:          &startedAt,
		EndedAt:            &now,
		DurationSeconds:    &duration,
		Players:            players,
	}

	go func() {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		if err := s.tournament.SaveMatchRecord(ctx, payload); err != nil {
			slog.Error("failed to save match record via webhook",
				"session", s.ID,
				"error", err,
			)
		}
	}()
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
		currentPlayer := s.Players[s.TurnIndex]
		payload.CurrentTurn = currentPlayer.ID

		// If the current player already has MaxPiecesPerPlayer pieces, their
		// oldest piece will be removed when they play next. Show it in advance.
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
