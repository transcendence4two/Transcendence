package logging

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net"
	"sync"
	"time"
)

type sharedConn struct {
	mu   sync.Mutex
	conn net.Conn
}

type logstashHandler struct {
	serviceName string
	serviceEnv  string
	addr        string

	shared *sharedConn

	attrs  []slog.Attr
	groups []string
}

func newLogstashHandler(host string, port int, serviceName, serviceEnv string) *logstashHandler {
	h := &logstashHandler{
		serviceName: serviceName,
		serviceEnv:  serviceEnv,
		addr:        fmt.Sprintf("%s:%d", host, port),
		shared:      &sharedConn{},
	}
	h.connect()
	return h
}

func (h *logstashHandler) connect() {
	if h.shared.conn != nil {
		_ = h.shared.conn.Close()
		h.shared.conn = nil
	}
	conn, err := net.DialTimeout("tcp", h.addr, 5*time.Second)
	if err != nil {
		return
	}
	h.shared.conn = conn
}

func (h *logstashHandler) Enabled(_ context.Context, _ slog.Level) bool {
	return true
}

func (h *logstashHandler) Handle(_ context.Context, r slog.Record) error {
	m := make(map[string]any, 8+r.NumAttrs())

	// ECS base fields
	m["@timestamp"] = r.Time.UTC().Format(time.RFC3339Nano)
	m["log.level"] = levelString(r.Level)
	m["message"] = r.Message
	m["service.name"] = h.serviceName
	m["service.environment"] = h.serviceEnv

	for _, a := range h.attrs {
		applyAttr(m, a, h.groups)
	}

	r.Attrs(func(a slog.Attr) bool {
		applyAttr(m, a, h.groups)
		return true
	})

	data, err := json.Marshal(m)
	if err != nil {
		return err
	}
	data = append(data, '\n')

	h.shared.mu.Lock()
	defer h.shared.mu.Unlock()

	if err := h.write(data); err != nil {
		h.connect()
		_ = h.write(data)
	}
	return nil
}

func (h *logstashHandler) write(data []byte) error {
	if h.shared.conn == nil {
		return io.ErrClosedPipe
	}
	_ = h.shared.conn.SetWriteDeadline(time.Now().Add(2 * time.Second))
	_, err := h.shared.conn.Write(data)
	return err
}

func (h *logstashHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
	clone := h.clone()
	clone.attrs = append(clone.attrs, attrs...)
	return clone
}

func (h *logstashHandler) WithGroup(name string) slog.Handler {
	clone := h.clone()
	clone.groups = append(clone.groups, name)
	return clone
}

func (h *logstashHandler) clone() *logstashHandler {
	return &logstashHandler{
		serviceName: h.serviceName,
		serviceEnv:  h.serviceEnv,
		addr:        h.addr,
		shared:      h.shared, // shared pointer — all clones use the same mutex + conn
		attrs:       append([]slog.Attr(nil), h.attrs...),
		groups:      append([]string(nil), h.groups...),
	}
}

type fanOutHandler struct {
	handlers []slog.Handler
}

func (f *fanOutHandler) Enabled(ctx context.Context, level slog.Level) bool {
	for _, h := range f.handlers {
		if h.Enabled(ctx, level) {
			return true
		}
	}
	return false
}

func (f *fanOutHandler) Handle(ctx context.Context, r slog.Record) error {
	var first error
	for _, h := range f.handlers {
		if h.Enabled(ctx, r.Level) {
			if err := h.Handle(ctx, r.Clone()); err != nil && first == nil {
				first = err
			}
		}
	}
	return first
}

func (f *fanOutHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
	handlers := make([]slog.Handler, len(f.handlers))
	for i, h := range f.handlers {
		handlers[i] = h.WithAttrs(attrs)
	}
	return &fanOutHandler{handlers: handlers}
}

func (f *fanOutHandler) WithGroup(name string) slog.Handler {
	handlers := make([]slog.Handler, len(f.handlers))
	for i, h := range f.handlers {
		handlers[i] = h.WithGroup(name)
	}
	return &fanOutHandler{handlers: handlers}
}

func applyAttr(m map[string]any, a slog.Attr, groups []string) {
	a.Value = a.Value.Resolve()
	if a.Equal(slog.Attr{}) {
		return
	}

	key := a.Key
	if len(groups) > 0 {
		buf := &bytes.Buffer{}
		for _, g := range groups {
			buf.WriteString(g)
			buf.WriteByte('.')
		}
		buf.WriteString(key)
		key = buf.String()
	}

	if a.Value.Kind() == slog.KindGroup {
		for _, ga := range a.Value.Group() {
			subGroups := append(groups, a.Key)
			applyAttr(m, ga, subGroups)
		}
		return
	}

	m[key] = a.Value.Any()
}

func levelString(l slog.Level) string {
	switch {
	case l >= slog.LevelError:
		return "ERROR"
	case l >= slog.LevelWarn:
		return "WARN"
	case l >= slog.LevelInfo:
		return "INFO"
	default:
		return "DEBUG"
	}
}
