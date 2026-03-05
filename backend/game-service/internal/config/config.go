package config

import (
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"

	"github.com/joho/godotenv"
)

func init() {
	// Locate the project root .env relative to this source file.
	// This works both with `go run` and compiled binaries launched from the
	// game-service directory (../../.env).
	_, thisFile, _, ok := runtime.Caller(0)
	if ok {
		root := filepath.Join(filepath.Dir(thisFile), "..", "..", "..", "..")
		_ = godotenv.Load(filepath.Join(root, ".env"))
	}

	// Also try ../../.env relative to the working directory (covers `go run`
	// from backend/game-service/).
	_ = godotenv.Load("../../.env")
}

type Config struct {
	ServerPort           int
	LogLevel             string
	TournamentServiceURL string
	WebhookSharedSecret  string
	AllowedOrigins       []string
}

func Load() Config {
	return Config{
		ServerPort:           getEnvInt("SERVER_PORT", 8001),
		LogLevel:             getEnv("LOG_LEVEL", "info"),
		TournamentServiceURL: getEnv("TOURNAMENT_SERVICE_URL", "http://tournament-service:8002"),
		WebhookSharedSecret:  getEnv("WEBHOOK_SHARED_SECRET", "local-webhook-token"),
		AllowedOrigins:       parseOrigins(getEnv("ALLOWED_ORIGINS", "")),
	}
}

func parseOrigins(raw string) []string {
	if raw == "" {
		return nil
	}
	parts := strings.Split(raw, ",")
	origins := make([]string, 0, len(parts))
	for _, p := range parts {
		if trimmed := strings.TrimSpace(p); trimmed != "" {
			origins = append(origins, trimmed)
		}
	}
	return origins
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func getEnvInt(key string, fallback int) int {
	v := os.Getenv(key)
	if v == "" {
		return fallback
	}
	i, err := strconv.Atoi(v)
	if err != nil {
		return fallback
	}
	return i
}
