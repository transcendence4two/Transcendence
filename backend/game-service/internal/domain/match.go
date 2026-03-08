package domain

import "time"

const (
	RoundsToWin    = 2
	RoundResetDelay = 3 * time.Second
)

type MatchScore [2]int

func (s *MatchScore) RecordWin(playerIndex int) {
	if playerIndex >= 0 && playerIndex < 2 {
		s[playerIndex]++
	}
}

func (s MatchScore) IsDecided() bool {
	return s[0] >= RoundsToWin || s[1] >= RoundsToWin
}

func (s MatchScore) WinnerIndex() int {
	if s[0] >= RoundsToWin {
		return 0
	}
	if s[1] >= RoundsToWin {
		return 1
	}
	return -1
}
