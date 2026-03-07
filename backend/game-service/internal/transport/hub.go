package transport

import (
	"encoding/json"
	"log/slog"
	"sync"

	"github.com/transcendence4two/Transcendence/backend/game-service/internal/config"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/protocol"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/session"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/tournament"
)

type Hub struct {
	mu      sync.RWMutex
	clients map[*Client]bool
	rooms   map[string]map[*Client]bool // sessionID → set of clients

	register   chan *Client
	unregister chan *Client

	sessionMgr *session.Manager
	config     config.Config
}

func NewHub(tc tournament.Client, cfg config.Config) *Hub {
	h := &Hub{
		clients:    make(map[*Client]bool),
		rooms:      make(map[string]map[*Client]bool),
		register:   make(chan *Client),
		unregister: make(chan *Client),
		config:     cfg,
	}
	h.sessionMgr = session.NewManager(h.BroadcastToSession, h.NotifyPlayer, tc)
	return h
}

func (h *Hub) SessionManager() *session.Manager {
	return h.sessionMgr
}

func (h *Hub) Config() config.Config {
	return h.config
}

func (h *Hub) Run() {
	slog.Info("hub started")
	for {
		select {
		case client := <-h.register:
			h.mu.Lock()
			h.clients[client] = true
			if client.SessionID != "" {
				room, ok := h.rooms[client.SessionID]
				if !ok {
					room = make(map[*Client]bool)
					h.rooms[client.SessionID] = room
				}
				room[client] = true
			}
			h.mu.Unlock()
			slog.Info("client registered", "player", client.PlayerID, "session", client.SessionID)

		case client := <-h.unregister:
			h.mu.Lock()
			if _, ok := h.clients[client]; ok {
				delete(h.clients, client)
				if client.SessionID != "" {
					if room, ok := h.rooms[client.SessionID]; ok {
						delete(room, client)
						if len(room) == 0 {
							delete(h.rooms, client.SessionID)
						}
					}
				}
				close(client.send)
			}
			h.mu.Unlock()
			slog.Info("client unregistered", "player", client.PlayerID, "session", client.SessionID)

			if client.SessionID != "" && client.PlayerID != "" {
				if sess, err := h.sessionMgr.GetSession(client.SessionID); err == nil {
					sess.Disconnect(client.PlayerID)
				}
			}
		}
	}
}

func HandleMessage(hub *Hub, client *Client, raw []byte) {
	var msg protocol.ClientMessage
	if err := json.Unmarshal(raw, &msg); err != nil {
		slog.Warn("invalid message format", "error", err, "player", client.PlayerID)
		hub.SendError(client, "invalid message format")
		return
	}

	switch msg.Type {
	case protocol.TypeJoin:
		handleJoin(hub, client, msg.Payload)
	case protocol.TypeMove:
		handleMove(hub, client, msg.Payload)
	default:
		slog.Warn("unknown message type", "type", msg.Type, "player", client.PlayerID)
		hub.SendError(client, "unknown message type: "+msg.Type)
	}
}

func handleJoin(hub *Hub, client *Client, payload json.RawMessage) {
	var join protocol.JoinPayload
	if err := json.Unmarshal(payload, &join); err != nil {
		hub.SendError(client, "invalid join payload")
		return
	}

	if join.PlayerID == "" {
		hub.SendError(client, "player_id is required")
		return
	}

	client.PlayerID = join.PlayerID

	sess := hub.SessionManager().GetOrCreateSession(client.SessionID)
	if _, err := sess.Join(join.PlayerID); err != nil {
		hub.SendError(client, err.Error())
		return
	}

	slog.Info("player joined session", "player", join.PlayerID, "session", client.SessionID)
}

func handleMove(hub *Hub, client *Client, payload json.RawMessage) {
	var move protocol.MovePayload
	if err := json.Unmarshal(payload, &move); err != nil {
		hub.SendError(client, "invalid move payload")
		return
	}

	sess, err := hub.SessionManager().GetSession(client.SessionID)
	if err != nil {
		hub.SendError(client, err.Error())
		return
	}

	if err := sess.HandleMove(client.PlayerID, move.Row, move.Col); err != nil {
		hub.SendError(client, err.Error())
		return
	}
}

func (h *Hub) BroadcastToSession(sessionID string, msg protocol.ServerMessage) {
	data, err := json.Marshal(msg)
	if err != nil {
		slog.Error("failed to marshal broadcast", "error", err)
		return
	}

	h.mu.RLock()
	defer h.mu.RUnlock()

	room, ok := h.rooms[sessionID]
	if !ok {
		return
	}

	for client := range room {
		select {
		case client.send <- data:
		default:
			slog.Warn("client send buffer full, dropping message", "player", client.PlayerID)
		}
	}
}

func (h *Hub) NotifyPlayer(playerID string, msg protocol.ServerMessage) {
	data, err := json.Marshal(msg)
	if err != nil {
		slog.Error("failed to marshal notification", "error", err)
		return
	}

	h.mu.RLock()
	defer h.mu.RUnlock()

	for _, room := range h.rooms {
		for client := range room {
			if client.PlayerID == playerID {
				select {
				case client.send <- data:
				default:
					slog.Warn("client send buffer full, dropping message", "player", playerID)
				}
				return
			}
		}
	}
}

func (h *Hub) SendError(client *Client, message string) {
	msg := protocol.ServerMessage{
		Type:    protocol.TypeError,
		Payload: protocol.ErrorPayload{Message: message},
	}
	data, err := json.Marshal(msg)
	if err != nil {
		return
	}
	select {
	case client.send <- data:
	default:
	}
}
