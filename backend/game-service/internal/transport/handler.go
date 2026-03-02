package transport

import (
	"encoding/json"
	"log/slog"
	"net/http"

	"github.com/gorilla/websocket"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/session"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		// TODO: restrict to allowed origins in production
		return true
	},
}

func RegisterRoutes(mux *http.ServeMux, hub *Hub) {
	mux.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
		handleWebSocket(hub, w, r)
	})
	mux.HandleFunc("/health", handleHealth)
	mux.HandleFunc("/api/sessions", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, `{"error":"method not allowed"}`, http.StatusMethodNotAllowed)
			return
		}
		handleCreateSession(hub, w, r)
	})
}

func handleWebSocket(hub *Hub, w http.ResponseWriter, r *http.Request) {
	sessionID := r.URL.Query().Get("session_id")
	if sessionID == "" {
		http.Error(w, `{"error":"session_id query parameter is required"}`, http.StatusBadRequest)
		return
	}

	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		slog.Error("websocket upgrade failed", "error", err)
		return
	}

	client := NewClient(hub, conn, sessionID)
	hub.register <- client

	go client.WritePump()
	go client.ReadPump()
}

type CreateSessionRequest struct {
	TournamentID string            `json:"tournament_id"`
	MatchID      string            `json:"match_id"`
	Players      []PlayerMapping   `json:"players"`
}

type PlayerMapping struct {
	UserID        string `json:"user_id"`
	ParticipantID string `json:"participant_id"`
}

type CreateSessionResponse struct {
	SessionID string `json:"session_id"`
}

// handleCreateSession is called by tournament-service to pre-create a game session
// with tournament context before players connect via WebSocket.
func handleCreateSession(hub *Hub, w http.ResponseWriter, r *http.Request) {
	var req CreateSessionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"error":"invalid request body"}`, http.StatusBadRequest)
		return
	}

	if req.TournamentID == "" || req.MatchID == "" || len(req.Players) != 2 {
		http.Error(w, `{"error":"tournament_id, match_id, and exactly 2 players are required"}`, http.StatusBadRequest)
		return
	}

	participantMap := make(map[string]string, len(req.Players))
	for _, p := range req.Players {
		participantMap[p.UserID] = p.ParticipantID
	}

	cfg := &session.SessionConfig{
		TournamentID:   req.TournamentID,
		MatchID:        req.MatchID,
		ParticipantMap: participantMap,
	}

	sessionID := hub.SessionManager().CreateSessionWithConfig(cfg)

	slog.Info("tournament session created",
		"session_id", sessionID,
		"tournament_id", req.TournamentID,
		"match_id", req.MatchID,
	)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(CreateSessionResponse{SessionID: sessionID})
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "ok",
		"service": "game-service",
	})
}
