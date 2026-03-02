package session

// SessionConfig holds optional tournament context for a game session.
// When present, the game-service will report the match result
// to the tournament-service upon game completion.
type SessionConfig struct {
	TournamentID   string            `json:"tournament_id"`
	MatchID        string            `json:"match_id"`
	ParticipantMap map[string]string `json:"participant_map"` // user_id → participant_id
}
