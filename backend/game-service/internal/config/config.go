package config

import (
	"os"
	"strconv"
)

type Config struct {
	ServerPort           int
	LogLevel             string
	TournamentServiceURL string
}

func Load() Config {
	return Config{
		ServerPort:           getEnvInt("SERVER_PORT", 8001),
		LogLevel:             getEnv("LOG_LEVEL", "info"),
		TournamentServiceURL: getEnv("TOURNAMENT_SERVICE_URL", "http://tournament-service:8002"),
	}
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
