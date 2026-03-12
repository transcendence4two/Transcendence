package session

import (
	"log/slog"
	"time"

	"github.com/transcendence4two/Transcendence/backend/game-service/internal/domain"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/protocol"
)

func (s *Session) finishRound(winnerID, reason string, line []domain.Position) {
	winnerIdx := s.playerIndex(winnerID)
	s.Score.RecordWin(winnerIdx)

	slog.Info("round finished",
		"session", s.ID,
		"round", s.Round,
		"winner", winnerID,
		"score", s.Score,
	)

	winningLine := protocol.ToPositionDTOs(line)

	roundPayload := protocol.RoundOverPayload{
		WinnerID:    winnerID,
		Reason:      reason,
		Board:       s.Board.ToStrings(),
		WinningLine: winningLine,
		Round:       s.Round,
		Score:       s.Score,
	}

	s.broadcast(s.ID, protocol.ServerMessage{
		Type:    protocol.TypeRoundOver,
		Payload: roundPayload,
	})

	if s.Score.IsDecided() {
		s.finishMatch(winnerID, reason, line)
		return
	}

	nextStarter := 1 - winnerIdx

	s.roundResetTimer = time.AfterFunc(domain.RoundResetDelay, func() {
		s.mu.Lock()
		defer s.mu.Unlock()

		if s.State != domain.StatePlaying {
			return
		}

		s.resetRound(nextStarter)
	})
}

func (s *Session) finishMatch(winnerID, reason string, line []domain.Position) {
	s.State = domain.StateFinished

	s.cleanupTimers()

	var loserID string
	for _, p := range s.Players {
		if p != nil && p.ID != winnerID {
			loserID = p.ID
		}
	}

	slog.Info("match finished",
		"session", s.ID,
		"winner", winnerID,
		"reason", reason,
		"score", s.Score,
	)

	s.broadcast(s.ID, protocol.ServerMessage{
		Type: protocol.TypeGameOver,
		Payload: protocol.GameOverPayload{
			WinnerID:    winnerID,
			Reason:      reason,
			Board:       s.Board.ToStrings(),
			WinningLine: protocol.ToPositionDTOs(line),
			Score:       s.Score,
		},
	})

	s.reportToTournament(winnerID, loserID)
}

func (s *Session) resetRound(nextStarterIndex int) {
	s.Round++
	s.Board = domain.NewBoard()
	s.MoveHistory = domain.NewMoveHistory()
	s.lastRemoved = nil
	s.TurnIndex = nextStarterIndex

	slog.Info("round reset",
		"session", s.ID,
		"round", s.Round,
		"starting_player", s.Players[s.TurnIndex].ID,
	)

	s.broadcastState()
}

func (s *Session) cleanupTimers() {
	for pid, timer := range s.disconnectedPlayers {
		if timer != nil {
			timer.Stop()
		}
		delete(s.disconnectedPlayers, pid)
	}
	if s.roundResetTimer != nil {
		s.roundResetTimer.Stop()
		s.roundResetTimer = nil
	}
}
