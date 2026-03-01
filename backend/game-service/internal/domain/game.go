package domain

import "time"

type Symbol string

const (
	SymbolX     Symbol = "X"
	SymbolO     Symbol = "O"
	SymbolEmpty Symbol = ""
)

type GameState int

const (
	StateWaiting  GameState = iota
	StatePlaying
	StateFinished
)

func (s GameState) String() string {
	switch s {
	case StateWaiting:
		return "waiting"
	case StatePlaying:
		return "playing"
	case StateFinished:
		return "finished"
	default:
		return "unknown"
	}
}

const BoardSize = 3

type Board [BoardSize][BoardSize]Symbol

func NewBoard() Board {
	return Board{}
}

type Player struct {
	ID     string `json:"id"`
	Symbol Symbol `json:"symbol"`
}

type Move struct {
	PlayerID string `json:"player_id"`
	Row      int    `json:"row"`
	Col      int    `json:"col"`
}

type GameResult struct {
	SessionID string    `json:"session_id"`
	WinnerID  string    `json:"winner_id,omitempty"`
	LoserID   string    `json:"loser_id,omitempty"`
	IsDraw    bool      `json:"is_draw"`
	Reason    string    `json:"reason"`
	Board     Board     `json:"board"`
	StartedAt time.Time `json:"started_at"`
	EndedAt   time.Time `json:"ended_at"`
}
