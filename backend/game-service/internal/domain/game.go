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

const (
	BoardSize          = 3
	MaxPiecesPerPlayer = 3
)

type Board [BoardSize][BoardSize]Symbol

func NewBoard() Board {
	return Board{}
}

func (b Board) ToStrings() [BoardSize][BoardSize]string {
	var out [BoardSize][BoardSize]string
	for i := 0; i < BoardSize; i++ {
		for j := 0; j < BoardSize; j++ {
			out[i][j] = string(b[i][j])
		}
	}
	return out
}

type Position struct {
	Row int `json:"row"`
	Col int `json:"col"`
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

type MoveHistory map[Symbol][]Position

func NewMoveHistory() MoveHistory {
	return MoveHistory{
		SymbolX: {},
		SymbolO: {},
	}
}

type GameResult struct {
	SessionID string    `json:"session_id"`
	WinnerID  string    `json:"winner_id"`
	LoserID   string    `json:"loser_id"`
	Reason    string    `json:"reason"`
	Board     Board     `json:"board"`
	StartedAt time.Time `json:"started_at"`
	EndedAt   time.Time `json:"ended_at"`
}
