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

type Client interface {
	ReportResult(ctx context.Context, tournamentID, matchID string, payload MatchResultPayload) error
}

type HTTPClient struct {
	baseURL    string
	httpClient *http.Client
}

func NewHTTPClient(baseURL string) *HTTPClient {
	return &HTTPClient{
		baseURL: baseURL,
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
