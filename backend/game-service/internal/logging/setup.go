package logging

import (
	"log/slog"
	"os"

	"github.com/transcendence4two/Transcendence/backend/game-service/internal/config"
)

const serviceName = "game-service"

func Setup(cfg config.Config) *slog.Logger {
	level := parseLevel(cfg.LogLevel)

	stdoutHandler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: level,
	})

	logstash := newLogstashHandler(cfg.LogstashHost, cfg.LogstashPort, serviceName, cfg.ServiceEnvironment)

	fan := &fanOutHandler{
		handlers: []slog.Handler{stdoutHandler, logstash},
	}

	logger := slog.New(fan)
	slog.SetDefault(logger)
	return logger
}

func parseLevel(s string) slog.Level {
	switch s {
	case "debug":
		return slog.LevelDebug
	case "warn", "warning":
		return slog.LevelWarn
	case "error":
		return slog.LevelError
	default:
		return slog.LevelInfo
	}
}
