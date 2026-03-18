package transport

import (
	"context"
	"log/slog"
	"net/http"

	"github.com/google/uuid"
)

type contextKey struct{}

func LoggerFromContext(ctx context.Context) *slog.Logger {
	if l, ok := ctx.Value(contextKey{}).(*slog.Logger); ok {
		return l
	}
	return slog.Default()
}

func WithRequestContext(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requestID := uuid.New().String()

		logger := slog.Default().With(
			"http.request.id", requestID,
			"trace.id", requestID,
			"http.request.method", r.Method,
			"url.path", r.URL.Path,
			"url.route", r.URL.Path,
			"client.address", r.RemoteAddr,
			"user_agent.original", r.UserAgent(),
		)

		ctx := context.WithValue(r.Context(), contextKey{}, logger)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
