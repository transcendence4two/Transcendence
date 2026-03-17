package transport

import (
	"encoding/json"
	"log/slog"
	"net/http"

	"github.com/gorilla/websocket"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/session"
)

func newUpgrader(allowedOrigins []string) websocket.Upgrader {
	return websocket.Upgrader{
		ReadBufferSize:  1024,
		WriteBufferSize: 1024,
		CheckOrigin: func(r *http.Request) bool {
			if len(allowedOrigins) == 0 {
				return true // no restriction configured — allow all (dev mode)
			}
			origin := r.Header.Get("Origin")
			for _, allowed := range allowedOrigins {
				if origin == allowed {
					return true
				}
			}
			slog.Warn("websocket origin rejected", "origin", origin)
			return false
		},
	}
}

func RegisterRoutes(mux *http.ServeMux, hub *Hub) {
	mux.Handle("/ws", WithRequestContext(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		handleWebSocket(hub, w, r)
	})))
	mux.Handle("/health", WithRequestContext(http.HandlerFunc(handleHealth)))
	mux.Handle("/api/sessions", WithRequestContext(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, `{"error":"method not allowed"}`, http.StatusMethodNotAllowed)
			return
		}
		handleCreateSession(hub, w, r)
	})))
	mux.Handle("/api/sessions/active", WithRequestContext(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, `{"error":"method not allowed"}`, http.StatusMethodNotAllowed)
			return
		}
		handleActiveSession(hub, w, r)
	})))
}

func handleWebSocket(hub *Hub, w http.ResponseWriter, r *http.Request) {
	sessionID := r.URL.Query().Get("session_id")
	if sessionID == "" {
		http.Error(w, `{"error":"session_id query parameter is required"}`, http.StatusBadRequest)
		return
	}

	upgrader := newUpgrader(hub.Config().AllowedOrigins)
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		LoggerFromContext(r.Context()).Error("websocket upgrade failed", "error", err)
		return
	}

	client := NewClient(hub, conn, sessionID)
	hub.register <- client

	go client.WritePump()
	go client.ReadPump()
}

type CreateSessionRequest struct {
	TournamentID string          `json:"tournament_id"`
	MatchID      string          `json:"match_id"`
	Players      []PlayerMapping `json:"players"`
}

type PlayerMapping struct {
	UserID        string `json:"user_id"`
	ParticipantID string `json:"participant_id"`
}

type CreateSessionResponse struct {
	SessionID string `json:"session_id"`
}

func handleCreateSession(hub *Hub, w http.ResponseWriter, r *http.Request) {
	var req CreateSessionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"error":"invalid request body"}`, http.StatusBadRequest)
		return
	}

	if len(req.Players) != 2 {
		http.Error(w, `{"error":"exactly 2 players are required"}`, http.StatusBadRequest)
		return
	}

	participantMap := make(map[string]string, len(req.Players))
	for _, p := range req.Players {
		participantMap[p.UserID] = p.ParticipantID
	}

	cfg := &session.Config{
		TournamentID:   req.TournamentID,
		MatchID:        req.MatchID,
		ParticipantMap: participantMap,
	}

	sessionID := hub.SessionManager().CreateSessionWithConfig(cfg)

	LoggerFromContext(r.Context()).Info("tournament session created",
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

type ActiveSessionResponse struct {
	SessionID string `json:"session_id"`
	State     string `json:"state"`
}

func handleActiveSession(hub *Hub, w http.ResponseWriter, r *http.Request) {
	playerID := r.URL.Query().Get("player_id")
	if playerID == "" {
		http.Error(w, `{"error":"player_id query parameter is required"}`, http.StatusBadRequest)
		return
	}

	sess := hub.SessionManager().FindActiveSessionByPlayer(playerID)
	if sess == nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{"error": "no active session"})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(ActiveSessionResponse{
		SessionID: sess.ID,
		State:     "playing",
	})
}
