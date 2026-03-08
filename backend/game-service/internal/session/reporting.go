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

	winnerScore, loserScore := 1, 0

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
