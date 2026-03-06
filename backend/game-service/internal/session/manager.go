package session

import (
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/domain"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/tournament"
)

const (
	SessionCleanupInterval = 1 * time.Minute
	FinishedSessionTTL = 30 * time.Second
	OrphanSessionTTL = 5 * time.Minute
)

type Manager struct {
	mu       sync.RWMutex
	sessions map[string]*Session

	broadcast  BroadcastFunc
	notify     NotifyFunc
	tournament tournament.Client
}

func NewManager(broadcast BroadcastFunc, notify NotifyFunc, tc tournament.Client) *Manager {
	m := &Manager{
		sessions:   make(map[string]*Session),
		broadcast:  broadcast,
		notify:     notify,
		tournament: tc,
	}
	go m.cleanupLoop()
	return m
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

func (m *Manager) FindActiveSessionByPlayer(playerID string) *Session {
	m.mu.RLock()
	defer m.mu.RUnlock()

	for _, sess := range m.sessions {
		sess.mu.Lock()
		state := sess.State
		var isPlayer bool
		for _, p := range sess.Players {
			if p != nil && p.ID == playerID {
				isPlayer = true
				break
			}
		}
		sess.mu.Unlock()

		if isPlayer && state == domain.StatePlaying {
			return sess
		}
	}
	return nil
}

func (m *Manager) cleanupLoop() {
	ticker := time.NewTicker(SessionCleanupInterval)
	defer ticker.Stop()

	for range ticker.C {
		m.cleanup()
	}
}

func (m *Manager) cleanup() {
	now := time.Now()

	m.mu.Lock()
	defer m.mu.Unlock()

	for id, sess := range m.sessions {
		sess.mu.Lock()
		state := sess.State
		createdAt := sess.CreatedAt
		sess.mu.Unlock()

		switch state {
		case domain.StateFinished:
			if now.Sub(createdAt) > FinishedSessionTTL {
				delete(m.sessions, id)
				slog.Info("cleaned up finished session", "session_id", id)
			}
		case domain.StateWaiting:
			if now.Sub(createdAt) > OrphanSessionTTL {
				delete(m.sessions, id)
				slog.Info("cleaned up orphan session", "session_id", id)
			}
		}
	}
}
