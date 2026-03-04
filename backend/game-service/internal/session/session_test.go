package session

import (
	"sync"
	"testing"
	"time"

	"github.com/transcendence4two/Transcendence/backend/game-service/internal/domain"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/protocol"
)

// collectMessages returns a BroadcastFunc that appends all messages to a slice (thread-safe).
func collectMessages() (BroadcastFunc, *[]protocol.ServerMessage, *sync.Mutex) {
	var mu sync.Mutex
	var msgs []protocol.ServerMessage
	return func(sessionID string, msg protocol.ServerMessage) {
		mu.Lock()
		defer mu.Unlock()
		msgs = append(msgs, msg)
	}, &msgs, &mu
}

func noopNotify(playerID string, msg protocol.ServerMessage) {}

// readSession safely reads session fields under the mutex.
type sessionSnapshot struct {
	State     domain.GameState
	Round     int
	Score     [2]int
	TurnIndex int
	Board     domain.Board
	MoveHistoryXLen int
	MoveHistoryOLen int
}

func takeSnapshot(s *Session) sessionSnapshot {
	s.mu.Lock()
	defer s.mu.Unlock()
	return sessionSnapshot{
		State:     s.State,
		Round:     s.Round,
		Score:     s.Score,
		TurnIndex: s.TurnIndex,
		Board:     s.Board,
		MoveHistoryXLen: len(s.MoveHistory[domain.SymbolX]),
		MoveHistoryOLen: len(s.MoveHistory[domain.SymbolO]),
	}
}

// setupPlayingSession creates a session with two players joined and game started.
func setupPlayingSession(t *testing.T) (*Session, *[]protocol.ServerMessage, *sync.Mutex) {
	t.Helper()
	broadcast, msgs, msgsMu := collectMessages()
	s := NewSession("test-session", broadcast, noopNotify, nil, nil)

	if _, err := s.Join("player1"); err != nil {
		t.Fatalf("player1 join failed: %v", err)
	}
	if _, err := s.Join("player2"); err != nil {
		t.Fatalf("player2 join failed: %v", err)
	}

	snap := takeSnapshot(s)
	if snap.State != domain.StatePlaying {
		t.Fatalf("expected StatePlaying, got %v", snap.State)
	}
	if snap.Round != 1 {
		t.Fatalf("expected round 1, got %d", snap.Round)
	}

	return s, msgs, msgsMu
}

// playWinForX plays a complete round where X wins (top row).
// Assumes X starts (TurnIndex == 0).
func playWinForX(t *testing.T, s *Session) {
	t.Helper()
	if err := s.HandleMove("player1", 0, 0); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	if err := s.HandleMove("player2", 1, 0); err != nil {
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
}

// playWinForO plays a complete round where O wins (middle row).
// Assumes O starts (TurnIndex == 1).
func playWinForO(t *testing.T, s *Session) {
	t.Helper()
	if err := s.HandleMove("player2", 1, 0); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	if err := s.HandleMove("player1", 0, 0); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	if err := s.HandleMove("player2", 1, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	if err := s.HandleMove("player1", 0, 1); err != nil {
		t.Fatalf("move failed: %v", err)
	}
	if err := s.HandleMove("player2", 1, 2); err != nil {
		t.Fatalf("move failed: %v", err)
	}
}

func waitForRoundReset() {
	time.Sleep(domain.RoundResetDelay + 500*time.Millisecond)
}

func TestMD3_WinnerAfterTwoRounds(t *testing.T) {
	s, _, _ := setupPlayingSession(t)

	// Round 1: X wins
	playWinForX(t, s)

	snap := takeSnapshot(s)
	if snap.Score[0] != 1 || snap.Score[1] != 0 {
		t.Fatalf("after round 1: expected score [1,0], got %v", snap.Score)
	}

	waitForRoundReset()

	snap = takeSnapshot(s)
	if snap.State != domain.StatePlaying {
		t.Fatalf("expected StatePlaying after round 1, got %v", snap.State)
	}
	if snap.Round != 2 {
		t.Fatalf("expected round 2, got %d", snap.Round)
	}
	if snap.TurnIndex != 1 {
		t.Fatalf("expected player2 (loser) to start round 2, got TurnIndex=%d", snap.TurnIndex)
	}

	// Board should be reset
	emptyBoard := domain.NewBoard()
	if snap.Board != emptyBoard {
		t.Fatal("board not reset after round 1")
	}

	// Round 2: O starts, X still wins
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

	snap = takeSnapshot(s)
	if snap.Score[0] != 2 || snap.Score[1] != 0 {
		t.Fatalf("after round 2: expected score [2,0], got %v", snap.Score)
	}
	if snap.State != domain.StateFinished {
		t.Fatalf("expected StateFinished after 2 wins, got %v", snap.State)
	}
}

func TestMD3_ThreeRoundsNeeded(t *testing.T) {
	s, _, _ := setupPlayingSession(t)

	// Round 1: X wins
	playWinForX(t, s)

	snap := takeSnapshot(s)
	if snap.Score != [2]int{1, 0} {
		t.Fatalf("after round 1: expected score [1,0], got %v", snap.Score)
	}

	waitForRoundReset()

	snap = takeSnapshot(s)
	if snap.Round != 2 {
		t.Fatalf("expected round 2, got %d", snap.Round)
	}

	// Round 2: O wins (O starts since X won round 1)
	playWinForO(t, s)

	snap = takeSnapshot(s)
	if snap.Score != [2]int{1, 1} {
		t.Fatalf("after round 2: expected score [1,1], got %v", snap.Score)
	}
	if snap.State != domain.StatePlaying {
		t.Fatalf("expected StatePlaying after tied series, got %v", snap.State)
	}

	waitForRoundReset()

	snap = takeSnapshot(s)
	if snap.Round != 3 {
		t.Fatalf("expected round 3, got %d", snap.Round)
	}
	if snap.TurnIndex != 0 {
		t.Fatalf("expected player1 (loser) to start round 3, got TurnIndex=%d", snap.TurnIndex)
	}

	// Round 3: X wins
	playWinForX(t, s)

	snap = takeSnapshot(s)
	if snap.Score != [2]int{2, 1} {
		t.Fatalf("after round 3: expected score [2,1], got %v", snap.Score)
	}
	if snap.State != domain.StateFinished {
		t.Fatalf("expected StateFinished, got %v", snap.State)
	}
}

func TestMD3_BoardResetsAfterRound(t *testing.T) {
	s, _, _ := setupPlayingSession(t)

	playWinForX(t, s)

	snap := takeSnapshot(s)
	if snap.State != domain.StatePlaying {
		t.Fatalf("expected StatePlaying (match not over), got %v", snap.State)
	}

	waitForRoundReset()

	snap = takeSnapshot(s)

	// Board should be fully empty
	emptyBoard := domain.NewBoard()
	if snap.Board != emptyBoard {
		t.Fatal("board was not reset after round")
	}

	// MoveHistory should be reset
	if snap.MoveHistoryXLen != 0 || snap.MoveHistoryOLen != 0 {
		t.Fatal("move history was not reset after round")
	}
}

func TestMD3_ForfeitEndsMatch(t *testing.T) {
	s, _, _ := setupPlayingSession(t)

	playWinForX(t, s)
	waitForRoundReset()

	// During round 2, player2 disconnects
	s.Disconnect("player2")

	// Wait for grace period
	time.Sleep(DisconnectGracePeriod + 500*time.Millisecond)

	snap := takeSnapshot(s)
	if snap.State != domain.StateFinished {
		t.Fatalf("expected StateFinished after forfeit, got %v", snap.State)
	}
}

func TestMD3_RoundOverMessages(t *testing.T) {
	s, msgs, msgsMu := setupPlayingSession(t)

	playWinForX(t, s)

	// Check that round_over message was sent
	msgsMu.Lock()
	msgsCopy := make([]protocol.ServerMessage, len(*msgs))
	copy(msgsCopy, *msgs)
	msgsMu.Unlock()

	foundRoundOver := false
	for _, msg := range msgsCopy {
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
	s, msgs, msgsMu := setupPlayingSession(t)

	// Win 2 rounds
	playWinForX(t, s)
	waitForRoundReset()

	// Clear messages to isolate round 2 messages
	msgsMu.Lock()
	*msgs = nil
	msgsMu.Unlock()

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

	// Read messages safely
	msgsMu.Lock()
	msgsCopy := make([]protocol.ServerMessage, len(*msgs))
	copy(msgsCopy, *msgs)
	msgsMu.Unlock()

	foundRoundOver := false
	foundGameOver := false
	for _, msg := range msgsCopy {
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
	broadcast, _, _ := collectMessages()
	s := NewSession("test", broadcast, noopNotify, nil, nil)

	snap := takeSnapshot(s)
	if snap.Round != 1 {
		t.Fatalf("expected initial round 1, got %d", snap.Round)
	}
	if snap.Score != [2]int{0, 0} {
		t.Fatalf("expected initial score [0,0], got %v", snap.Score)
	}
}
