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

func TestApplyMoveInfinity_NoPieceRemoved(t *testing.T) {
	board := NewBoard()
	history := NewMoveHistory()

	board, history, removed := ApplyMoveInfinity(board, 0, 0, SymbolX, history)
	if removed != nil {
		t.Fatal("expected no removal on first piece")
	}
	if board[0][0] != SymbolX {
		t.Fatal("expected X at (0,0)")
	}
	if len(history[SymbolX]) != 1 {
		t.Fatalf("expected 1 piece in history, got %d", len(history[SymbolX]))
	}
}

func TestApplyMoveInfinity_RemovesOldestAt4th(t *testing.T) {
	board := NewBoard()
	history := NewMoveHistory()

	// Place 3 X pieces
	board, history, _ = ApplyMoveInfinity(board, 0, 0, SymbolX, history) // oldest
	board, history, _ = ApplyMoveInfinity(board, 0, 1, SymbolX, history)
	board, history, _ = ApplyMoveInfinity(board, 0, 2, SymbolX, history)

	// Place 4th — should remove (0,0)
	board, history, removed := ApplyMoveInfinity(board, 1, 0, SymbolX, history)

	if removed == nil {
		t.Fatal("expected a piece to be removed")
	}
	if removed.Row != 0 || removed.Col != 0 {
		t.Fatalf("expected removal at (0,0), got (%d,%d)", removed.Row, removed.Col)
	}
	if board[0][0] != SymbolEmpty {
		t.Fatal("expected (0,0) to be empty after removal")
	}
	if board[1][0] != SymbolX {
		t.Fatal("expected X at (1,0)")
	}
	if len(history[SymbolX]) != 3 {
		t.Fatalf("expected 3 pieces in history, got %d", len(history[SymbolX]))
	}
}

func TestApplyMoveInfinity_IndependentPerPlayer(t *testing.T) {
	board := NewBoard()
	history := NewMoveHistory()

	// X places 3
	board, history, _ = ApplyMoveInfinity(board, 0, 0, SymbolX, history)
	board, history, _ = ApplyMoveInfinity(board, 0, 1, SymbolX, history)
	board, history, _ = ApplyMoveInfinity(board, 0, 2, SymbolX, history)

	// O places 1 — should NOT remove anything
	board, history, removed := ApplyMoveInfinity(board, 1, 0, SymbolO, history)
	if removed != nil {
		t.Fatal("O only has 1 piece, should not remove anything")
	}

	// X places 4th — removes X's oldest
	board, history, removed = ApplyMoveInfinity(board, 1, 1, SymbolX, history)
	if removed == nil || removed.Row != 0 || removed.Col != 0 {
		t.Fatal("should remove X's oldest at (0,0)")
	}

	if len(history[SymbolX]) != 3 {
		t.Fatalf("X should have 3 pieces, got %d", len(history[SymbolX]))
	}
	if len(history[SymbolO]) != 1 {
		t.Fatalf("O should have 1 piece, got %d", len(history[SymbolO]))
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

func TestWinAfterPieceRemoval(t *testing.T) {
	board := NewBoard()
	history := NewMoveHistory()

	// Build a scenario where X wins after piece removal
	// X: (0,0), (1,1), (2,2) — diagonal, but then X has to place 4th
	board, history, _ = ApplyMoveInfinity(board, 0, 0, SymbolX, history)
	board, history, _ = ApplyMoveInfinity(board, 1, 1, SymbolX, history)
	board, history, _ = ApplyMoveInfinity(board, 2, 2, SymbolX, history)

	// X has a diagonal win right now
	if w := CheckWinner(board); w != SymbolX {
		t.Fatalf("expected X to win with diagonal, got %s", w)
	}
}
