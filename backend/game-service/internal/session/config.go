package session

type Config struct {
	TournamentID   string            `json:"tournament_id"`
	MatchID        string            `json:"match_id"`
	ParticipantMap map[string]string `json:"participant_map"`
}
