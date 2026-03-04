package protocol

import "encoding/json"

// Client → Server

type ClientMessage struct {
	Type    string          `json:"type"`
	Payload json.RawMessage `json:"payload"`
}

type JoinPayload struct {
	PlayerID string `json:"player_id"`
}

type MovePayload struct {
	Row int `json:"row"`
	Col int `json:"col"`
}

// Server → Client

type ServerMessage struct {
	Type    string      `json:"type"`
	Payload interface{} `json:"payload"`
}

const (
	TypeJoin         = "join"
	TypeMove         = "move"
	TypeGameState    = "game_state"
	TypeGameOver     = "game_over"
	TypeRoundOver    = "round_over"
	TypeError        = "error"
	TypePlayerJoined = "player_joined"
	TypePlayerLeft   = "player_left"
)

type GameStatePayload struct {
	Board             [3][3]string `json:"board"`
	CurrentTurn       string       `json:"current_turn"`
	State             string       `json:"state"`
	Players           []PlayerInfo `json:"players"`
	RemovedPiece      *PositionDTO `json:"removed_piece,omitempty"`
	NextRemovedPiece  *PositionDTO `json:"next_removed_piece,omitempty"`
	Round             int          `json:"round"`
	Score             [2]int       `json:"score"`
}

type PositionDTO struct {
	Row int `json:"row"`
	Col int `json:"col"`
}

type PlayerInfo struct {
	ID     string `json:"id"`
	Symbol string `json:"symbol"`
}

type GameOverPayload struct {
	WinnerID    string         `json:"winner_id"`
	Reason      string         `json:"reason"`
	Board       [3][3]string   `json:"board"`
	WinningLine []PositionDTO  `json:"winning_line,omitempty"`
	Score       [2]int         `json:"score"`
}

type RoundOverPayload struct {
	WinnerID    string         `json:"winner_id"`
	Reason      string         `json:"reason"`
	Board       [3][3]string   `json:"board"`
	WinningLine []PositionDTO  `json:"winning_line,omitempty"`
	Round       int            `json:"round"`
	Score       [2]int         `json:"score"`
}

type ErrorPayload struct {
	Message string `json:"message"`
}

type PlayerJoinedPayload struct {
	PlayerID string `json:"player_id"`
	Symbol   string `json:"symbol"`
}

type PlayerLeftPayload struct {
	PlayerID string `json:"player_id"`
}
