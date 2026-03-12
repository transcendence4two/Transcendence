package domain

import (
	"errors"
	"fmt"
)

var (
	ErrOutOfBounds   = errors.New("position out of bounds")
	ErrCellTaken     = errors.New("cell is already occupied")
	ErrNotYourTurn   = errors.New("not your turn")
	ErrGameNotActive = errors.New("game is not active")
)

func ValidateMove(board Board, move Move) error {
	if move.Row < 0 || move.Row >= BoardSize || move.Col < 0 || move.Col >= BoardSize {
		return fmt.Errorf("%w: row=%d, col=%d", ErrOutOfBounds, move.Row, move.Col)
	}
	if board[move.Row][move.Col] != SymbolEmpty {
		return fmt.Errorf("%w: row=%d, col=%d", ErrCellTaken, move.Row, move.Col)
	}
	return nil
}

func ApplyMoveInfinity(board Board, row, col int, symbol Symbol, history MoveHistory) (Board, MoveHistory, *Position) {
	board[row][col] = symbol
	history[symbol] = append(history[symbol], Position{Row: row, Col: col})

	var removed *Position
	if len(history[symbol]) > MaxPiecesPerPlayer {
		oldest := history[symbol][0]
		board[oldest.Row][oldest.Col] = SymbolEmpty
		history[symbol] = history[symbol][1:]
		removed = &oldest
	}

	return board, history, removed
}

func CheckWinner(board Board) (Symbol, []Position) {
	for i := 0; i < BoardSize; i++ {
		if board[i][0] != SymbolEmpty && board[i][0] == board[i][1] && board[i][1] == board[i][2] {
			return board[i][0], []Position{{Row: i, Col: 0}, {Row: i, Col: 1}, {Row: i, Col: 2}}
		}
		if board[0][i] != SymbolEmpty && board[0][i] == board[1][i] && board[1][i] == board[2][i] {
			return board[0][i], []Position{{Row: 0, Col: i}, {Row: 1, Col: i}, {Row: 2, Col: i}}
		}
	}

	if board[0][0] != SymbolEmpty && board[0][0] == board[1][1] && board[1][1] == board[2][2] {
		return board[0][0], []Position{{Row: 0, Col: 0}, {Row: 1, Col: 1}, {Row: 2, Col: 2}}
	}
	if board[0][2] != SymbolEmpty && board[0][2] == board[1][1] && board[1][1] == board[2][0] {
		return board[0][2], []Position{{Row: 0, Col: 2}, {Row: 1, Col: 1}, {Row: 2, Col: 0}}
	}

	return SymbolEmpty, nil
}
