package tournament

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"time"
)

type MatchResultPayload struct {
	WinnerParticipantID string `json:"winner_participant_id"`
	PlayerOneScore      int    `json:"player_one_score"`
	PlayerTwoScore      int    `json:"player_two_score"`
}

type MatchPlayerSnapshot struct {
	UserID          string `json:"user_id"`
	DisplayName     string `json:"display_name"`
	ParticipantID   string `json:"participant_id,omitempty"`
	PlayerSide      string `json:"player_side,omitempty"`
	Score           int    `json:"score"`
	IsWinner        bool   `json:"is_winner"`
	DisconnectCount int    `json:"disconnect_count"`
}

type MatchRecordPayload struct {
	GameServiceMatchID string                `json:"game_service_match_id,omitempty"`
	TournamentID       string                `json:"tournament_id,omitempty"`
	TournamentMatchID  string                `json:"tournament_match_id,omitempty"`
	GameRoomID         string                `json:"game_room_id,omitempty"`
	GameMode           string                `json:"game_mode"`
	Status             string                `json:"status"`
	WinnerUserID       string                `json:"winner_user_id,omitempty"`
	WinningReason      string                `json:"winning_reason,omitempty"`
	StartedAt          *time.Time            `json:"started_at,omitempty"`
	EndedAt            *time.Time            `json:"ended_at,omitempty"`
	DurationSeconds    *int                  `json:"duration_seconds,omitempty"`
	Players            []MatchPlayerSnapshot `json:"players"`
}

type Client interface {
	ReportResult(ctx context.Context, tournamentID, matchID string, payload MatchResultPayload) error
	SaveMatchRecord(ctx context.Context, payload MatchRecordPayload) error
}

type HTTPClient struct {
	baseURL      string
	webhookToken string
	httpClient   *http.Client
}

func NewHTTPClient(baseURL, webhookToken string) *HTTPClient {
	return &HTTPClient{
		baseURL:      baseURL,
		webhookToken: webhookToken,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

func (c *HTTPClient) ReportResult(ctx context.Context, tournamentID, matchID string, payload MatchResultPayload) error {
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal result: %w", err)
	}

	url := fmt.Sprintf("%s/api/tournaments/%s/matches/%s/result", c.baseURL, tournamentID, matchID)

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return fmt.Errorf("tournament-service returned %d", resp.StatusCode)
	}

	slog.Info("match result reported",
		"tournament_id", tournamentID,
		"match_id", matchID,
		"winner", payload.WinnerParticipantID,
	)
	return nil
}

func (c *HTTPClient) SaveMatchRecord(ctx context.Context, payload MatchRecordPayload) error {
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal match record: %w", err)
	}

	url := fmt.Sprintf("%s/tournaments/webhooks/game-match-finished", c.baseURL)

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Webhook-Token", c.webhookToken)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return fmt.Errorf("tournament-service webhook returned %d", resp.StatusCode)
	}

	slog.Info("match record saved via webhook",
		"session_id", payload.GameServiceMatchID,
		"winner", payload.WinnerUserID,
	)
	return nil
}
