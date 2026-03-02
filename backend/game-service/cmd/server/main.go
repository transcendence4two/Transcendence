package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/transcendence4two/Transcendence/backend/game-service/internal/config"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/tournament"
	"github.com/transcendence4two/Transcendence/backend/game-service/internal/transport"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))
	slog.SetDefault(logger)

	cfg := config.Load()

	tc := tournament.NewHTTPClient(cfg.TournamentServiceURL)
	slog.Info("tournament client configured", "url", cfg.TournamentServiceURL)

	hub := transport.NewHub(tc)
	go hub.Run()

	mux := http.NewServeMux()
	transport.RegisterRoutes(mux, hub)

	addr := fmt.Sprintf(":%d", cfg.ServerPort)
	server := &http.Server{
		Addr:         addr,
		Handler:      mux,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	go func() {
		slog.Info("starting game-service", "address", addr)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			slog.Error("server error", "error", err)
			os.Exit(1)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	sig := <-quit
	slog.Info("shutting down", "signal", sig.String())

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		slog.Error("forced shutdown", "error", err)
	}

	slog.Info("game-service stopped")
}
