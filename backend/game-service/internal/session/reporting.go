package session

import (
	"context"
	"log/slog"
	"time"

	"github.com/transcendence4two/Transcendence/backend/game-service/internal/tournament"
)

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

	p1Score, p2Score := s.Score[0], s.Score[1]

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
		score := s.Score[i]
		isWinner := false
		if p.ID == winnerID {
			isWinner = true
		}
		players = append(players, tournament.MatchPlayerSnapshot{
			UserID:      p.ID,
			DisplayName: p.ID,
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
