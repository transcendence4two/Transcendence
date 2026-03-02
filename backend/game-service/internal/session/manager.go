package session

import (
	"fmt"
	"log/slog"
	"sync"

	"github.com/google/uuid"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/tournament"
)

type Manager struct {
	mu       sync.RWMutex
	sessions map[string]*Session

	broadcast  BroadcastFunc
	notify     NotifyFunc
	tournament tournament.Client
}

func NewManager(broadcast BroadcastFunc, notify NotifyFunc, tc tournament.Client) *Manager {
	return &Manager{
		sessions:   make(map[string]*Session),
		broadcast:  broadcast,
		notify:     notify,
		tournament: tc,
	}
}

func (m *Manager) CreateSession() string {
	return m.CreateSessionWithConfig(nil)
}

func (m *Manager) CreateSessionWithConfig(cfg *SessionConfig) string {
	m.mu.Lock()
	defer m.mu.Unlock()

	id := uuid.New().String()
	session := NewSession(id, m.broadcast, m.notify, m.tournament, cfg)
	m.sessions[id] = session

	slog.Info("session created", "session_id", id,
		"has_tournament_config", cfg != nil)
	return id
}

func (m *Manager) GetOrCreateSession(id string) *Session {
	m.mu.Lock()
	defer m.mu.Unlock()

	if session, ok := m.sessions[id]; ok {
		return session
	}

	session := NewSession(id, m.broadcast, m.notify, m.tournament, nil)
	m.sessions[id] = session
	slog.Info("session created on demand", "session_id", id)
	return session
}

func (m *Manager) GetSession(id string) (*Session, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	session, ok := m.sessions[id]
	if !ok {
		return nil, fmt.Errorf("session %s not found", id)
	}
	return session, nil
}

func (m *Manager) RemoveSession(id string) {
	m.mu.Lock()
	defer m.mu.Unlock()

	delete(m.sessions, id)
	slog.Info("session removed", "session_id", id)
}

func (m *Manager) Count() int {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return len(m.sessions)
}

func (m *Manager) ListSessionIDs() []string {
	m.mu.RLock()
	defer m.mu.RUnlock()

	ids := make([]string, 0, len(m.sessions))
	for id := range m.sessions {
		ids = append(ids, id)
	}
	return ids
}
