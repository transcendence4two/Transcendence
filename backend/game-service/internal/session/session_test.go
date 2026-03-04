package session

import (
	"sync"
	"testing"
	"time"

	"github.com/transcendence4two/Transcendence/backend/game-service/internal/domain"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/protocol"
)

// collectMessages returns a BroadcastFunc that appends all messages to a slice.
func collectMessages() (BroadcastFunc, *[]protocol.ServerMessage) {
	var mu sync.Mutex
	var msgs []protocol.ServerMessage
	return func(sessionID string, msg protocol.ServerMessage) {
		mu.Lock()
		defer mu.Unlock()
		msgs = append(msgs, msg)
	}, &msgs
}

func noopNotify(playerID string, msg protocol.ServerMessage) {}

// setupPlayingSession creates a session with two players joined and game started.
func setupPlayingSession(t *testing.T) (*Session, *[]protocol.ServerMessage) {
	t.Helper()
	broadcast, msgs := collectMessages()
	s := NewSession("test-session", broadcast, noopNotify, nil, nil)

	if _, err := s.Join("player1"); err != nil {
		t.Fatalf("player1 join failed: %v", err)
	}
	if _, err := s.Join("player2"); err != nil {
		t.Fatalf("player2 join failed: %v", err)
	}

	if s.State != domain.StatePlaying {
		t.Fatalf("expected StatePlaying, got %v", s.State)
	}
	if s.Round != 1 {
		t.Fatalf("expected round 1, got %d", s.Round)
	}

	return s, msgs
}

// playWinForX plays a complete round where X wins (top row).
// Assumes X starts (TurnIndex == 0).
func playWinForX(t *testing.T, s *Session) {
	t.Helper()
	// X plays (0,0)
	if err := s.HandleMove("player1", 0, 0); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// O plays (1,0)
	if err := s.HandleMove("player2", 1, 0); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// X plays (0,1)
	if err := s.HandleMove("player1", 0, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// O plays (1,1)
	if err := s.HandleMove("player2", 1, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// X plays (0,2) — X wins top row
	if err := s.HandleMove("player1", 0, 2); err != nil {
		t.Fatalf("move failed: %v", err)
	}
}

// playWinForO plays a complete round where O wins (middle row).
// Assumes O starts (TurnIndex == 1).
func playWinForO(t *testing.T, s *Session) {
	t.Helper()
	// O plays (1,0)
	if err := s.HandleMove("player2", 1, 0); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// X plays (0,0)
	if err := s.HandleMove("player1", 0, 0); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// O plays (1,1)
	if err := s.HandleMove("player2", 1, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// X plays (0,1)
	if err := s.HandleMove("player1", 0, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// O plays (1,2) — O wins middle row
	if err := s.HandleMove("player2", 1, 2); err != nil {
		t.Fatalf("move failed: %v", err)
	}
}

func TestMD3_WinnerAfterTwoRounds(t *testing.T) {
	s, _ := setupPlayingSession(t)

	// Round 1: X wins
	playWinForX(t, s)

	if s.Score[0] != 1 || s.Score[1] != 0 {
		t.Fatalf("after round 1: expected score [1,0], got %v", s.Score)
	}

	// Wait for round reset
	time.Sleep(domain.RoundResetDelay + 500*time.Millisecond)

	if s.State != domain.StatePlaying {
		t.Fatalf("expected StatePlaying after round 1, got %v", s.State)
	}
	if s.Round != 2 {
		t.Fatalf("expected round 2, got %d", s.Round)
	}

	// After round 1 where X won, loser (O, index 1) starts round 2
	if s.TurnIndex != 1 {
		t.Fatalf("expected player2 (loser) to start round 2, got TurnIndex=%d", s.TurnIndex)
	}

	// Board should be reset
	for i := 0; i < domain.BoardSize; i++ {
		for j := 0; j < domain.BoardSize; j++ {
			if s.Board[i][j] != domain.SymbolEmpty {
				t.Fatalf("board not reset at (%d,%d): %s", i, j, s.Board[i][j])
			}
		}
	}

	// Round 2: X wins again (but O starts, so we need a different sequence)
	// O plays (2,0)
	if err := s.HandleMove("player2", 2, 0); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// X plays (0,0)
	if err := s.HandleMove("player1", 0, 0); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// O plays (2,1)
	if err := s.HandleMove("player2", 2, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// X plays (0,1)
	if err := s.HandleMove("player1", 0, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// O plays (1,1) (not winning)
	if err := s.HandleMove("player2", 1, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	// X plays (0,2) — X wins top row again
	if err := s.HandleMove("player1", 0, 2); err != nil {
		t.Fatalf("move failed: %v", err)
	}

	if s.Score[0] != 2 || s.Score[1] != 0 {
		t.Fatalf("after round 2: expected score [2,0], got %v", s.Score)
	}
	if s.State != domain.StateFinished {
		t.Fatalf("expected StateFinished after 2 wins, got %v", s.State)
	}
}

func TestMD3_ThreeRoundsNeeded(t *testing.T) {
	s, _ := setupPlayingSession(t)

	// Round 1: X wins
	playWinForX(t, s)

	if s.Score != [2]int{1, 0} {
		t.Fatalf("after round 1: expected score [1,0], got %v", s.Score)
	}

	time.Sleep(domain.RoundResetDelay + 500*time.Millisecond)

	if s.Round != 2 {
		t.Fatalf("expected round 2, got %d", s.Round)
	}

	// Round 2: O wins (O starts since X won round 1)
	playWinForO(t, s)

	if s.Score != [2]int{1, 1} {
		t.Fatalf("after round 2: expected score [1,1], got %v", s.Score)
	}
	if s.State != domain.StatePlaying {
		t.Fatalf("expected StatePlaying after tied series, got %v", s.State)
	}

	time.Sleep(domain.RoundResetDelay + 500*time.Millisecond)

	if s.Round != 3 {
		t.Fatalf("expected round 3, got %d", s.Round)
	}

	// After round 2 where O won, loser (X, index 0) starts round 3
	if s.TurnIndex != 0 {
		t.Fatalf("expected player1 (loser) to start round 3, got TurnIndex=%d", s.TurnIndex)
	}

	// Round 3: X wins
	playWinForX(t, s)

	if s.Score != [2]int{2, 1} {
		t.Fatalf("after round 3: expected score [2,1], got %v", s.Score)
	}
	if s.State != domain.StateFinished {
		t.Fatalf("expected StateFinished, got %v", s.State)
	}
}

func TestMD3_BoardResetsAfterRound(t *testing.T) {
	s, _ := setupPlayingSession(t)

	playWinForX(t, s)

	// Immediately after round win, board should still have pieces
	// (it gets reset after RoundResetDelay)
	if s.State != domain.StatePlaying {
		t.Fatalf("expected StatePlaying (match not over), got %v", s.State)
	}

	time.Sleep(domain.RoundResetDelay + 500*time.Millisecond)

	// Board should be fully empty
	emptyBoard := domain.NewBoard()
	if s.Board != emptyBoard {
		t.Fatal("board was not reset after round")
	}

	// MoveHistory should be reset
	if len(s.MoveHistory[domain.SymbolX]) != 0 || len(s.MoveHistory[domain.SymbolO]) != 0 {
		t.Fatal("move history was not reset after round")
	}
}

func TestMD3_ForfeitEndsMatch(t *testing.T) {
	s, _ := setupPlayingSession(t)

	// Play round 1: X wins
	playWinForX(t, s)
	time.Sleep(domain.RoundResetDelay + 500*time.Millisecond)

	// During round 2, player2 disconnects
	s.Disconnect("player2")

	// Wait for grace period
	time.Sleep(DisconnectGracePeriod + 500*time.Millisecond)

	// Match should be finished (forfeit ends entire match)
	if s.State != domain.StateFinished {
		t.Fatalf("expected StateFinished after forfeit, got %v", s.State)
	}
}

func TestMD3_RoundOverMessages(t *testing.T) {
	s, msgs := setupPlayingSession(t)

	playWinForX(t, s)

	// Check that round_over message was sent
	foundRoundOver := false
	for _, msg := range *msgs {
		if msg.Type == protocol.TypeRoundOver {
			foundRoundOver = true
			payload, ok := msg.Payload.(protocol.RoundOverPayload)
			if !ok {
				t.Fatal("round_over payload has wrong type")
			}
			if payload.WinnerID != "player1" {
				t.Fatalf("expected winner player1, got %s", payload.WinnerID)
			}
			if payload.Round != 1 {
				t.Fatalf("expected round 1, got %d", payload.Round)
			}
			if payload.Score != [2]int{1, 0} {
				t.Fatalf("expected score [1,0], got %v", payload.Score)
			}
			break
		}
	}
	if !foundRoundOver {
		t.Fatal("round_over message was not broadcast")
	}
}

func TestMD3_GameOverAfterMatchWin(t *testing.T) {
	s, msgs := setupPlayingSession(t)

	// Win 2 rounds
	playWinForX(t, s)
	time.Sleep(domain.RoundResetDelay + 500*time.Millisecond)

	// Clear messages to isolate round 2 messages
	*msgs = nil

	// Round 2: O starts, X wins
	if err := s.HandleMove("player2", 2, 0); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	if err := s.HandleMove("player1", 0, 0); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	if err := s.HandleMove("player2", 2, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	if err := s.HandleMove("player1", 0, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	if err := s.HandleMove("player2", 1, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	if err := s.HandleMove("player1", 0, 2); err != nil {
		t.Fatalf("move failed: %v", err)
	}

	// Should have both round_over and game_over messages
	foundRoundOver := false
	foundGameOver := false
	for _, msg := range *msgs {
		if msg.Type == protocol.TypeRoundOver {
			foundRoundOver = true
		}
		if msg.Type == protocol.TypeGameOver {
			foundGameOver = true
			payload, ok := msg.Payload.(protocol.GameOverPayload)
			if !ok {
				t.Fatal("game_over payload has wrong type")
			}
			if payload.Score != [2]int{2, 0} {
				t.Fatalf("expected final score [2,0], got %v", payload.Score)
			}
		}
	}
	if !foundRoundOver {
		t.Fatal("round_over not sent before game_over on match-winning round")
	}
	if !foundGameOver {
		t.Fatal("game_over not sent after match decided")
	}
}

func TestMD3_InitialState(t *testing.T) {
	broadcast, _ := collectMessages()
	s := NewSession("test", broadcast, noopNotify, nil, nil)

	if s.Round != 1 {
		t.Fatalf("expected initial round 1, got %d", s.Round)
	}
	if s.Score != [2]int{0, 0} {
		t.Fatalf("expected initial score [0,0], got %v", s.Score)
	}
}
