package domain

import "testing"

func TestValidateMove_Valid(t *testing.T) {
	board := NewBoard()
	move := Move{PlayerID: "p1", Row: 0, Col: 0}
	if err := ValidateMove(board, move); err != nil {
		t.Fatalf("expected valid move, got error: %v", err)
	}
}

func TestValidateMove_OutOfBounds(t *testing.T) {
	board := NewBoard()
	cases := []Move{
		{Row: -1, Col: 0},
		{Row: 0, Col: -1},
		{Row: 3, Col: 0},
		{Row: 0, Col: 3},
	}
	for _, m := range cases {
		if err := ValidateMove(board, m); err == nil {
			t.Errorf("expected out of bounds error for row=%d col=%d", m.Row, m.Col)
		}
	}
}

func TestValidateMove_CellTaken(t *testing.T) {
	board := NewBoard()
	board[1][1] = SymbolX
	move := Move{PlayerID: "p1", Row: 1, Col: 1}
	if err := ValidateMove(board, move); err == nil {
		t.Fatal("expected cell taken error")
	}
}

func TestApplyMove(t *testing.T) {
	board := NewBoard()
	board = ApplyMove(board, 0, 0, SymbolX)
	if board[0][0] != SymbolX {
		t.Fatalf("expected X at (0,0), got %s", board[0][0])
	}
}

func TestCheckWinner_Row(t *testing.T) {
	board := NewBoard()
	board[0][0] = SymbolX
	board[0][1] = SymbolX
	board[0][2] = SymbolX
	if w := CheckWinner(board); w != SymbolX {
		t.Fatalf("expected X to win row, got %s", w)
	}
}

func TestCheckWinner_Column(t *testing.T) {
	board := NewBoard()
	board[0][1] = SymbolO
	board[1][1] = SymbolO
	board[2][1] = SymbolO
	if w := CheckWinner(board); w != SymbolO {
		t.Fatalf("expected O to win column, got %s", w)
	}
}

func TestCheckWinner_Diagonal(t *testing.T) {
	board := NewBoard()
	board[0][0] = SymbolX
	board[1][1] = SymbolX
	board[2][2] = SymbolX
	if w := CheckWinner(board); w != SymbolX {
		t.Fatalf("expected X to win diagonal, got %s", w)
	}
}

func TestCheckWinner_AntiDiagonal(t *testing.T) {
	board := NewBoard()
	board[0][2] = SymbolO
	board[1][1] = SymbolO
	board[2][0] = SymbolO
	if w := CheckWinner(board); w != SymbolO {
		t.Fatalf("expected O to win anti-diagonal, got %s", w)
	}
}

func TestCheckWinner_NoWinner(t *testing.T) {
	board := NewBoard()
	board[0][0] = SymbolX
	board[0][1] = SymbolO
	if w := CheckWinner(board); w != SymbolEmpty {
		t.Fatalf("expected no winner, got %s", w)
	}
}

func TestIsDraw(t *testing.T) {
	// X O X
	// X X O
	// O X O
	board := Board{
		{SymbolX, SymbolO, SymbolX},
		{SymbolX, SymbolX, SymbolO},
		{SymbolO, SymbolX, SymbolO},
	}
	if !IsDraw(board) {
		t.Fatal("expected draw")
	}
}

func TestIsDraw_NotFull(t *testing.T) {
	board := NewBoard()
	board[0][0] = SymbolX
	if IsDraw(board) {
		t.Fatal("board is not full, should not be a draw")
	}
}

func TestIsDraw_HasWinner(t *testing.T) {
	board := Board{
		{SymbolX, SymbolX, SymbolX},
		{SymbolO, SymbolO, SymbolEmpty},
		{SymbolEmpty, SymbolEmpty, SymbolEmpty},
	}
	if IsDraw(board) {
		t.Fatal("has a winner, should not be a draw")
	}
}
