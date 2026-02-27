from dataclasses import dataclass


@dataclass
class DomainError(Exception):
    """Base exception for domain errors."""

    message: str

    def __str__(self):
        return self.message


class TournamentNotFoundError(DomainError):
    """Tournament does not exist."""


class DatabaseError(DomainError):
    """Database operation failed."""


class TournamentStateError(DomainError):
    """Tournament is in an invalid state for the requested operation."""


class TournamentParticipantError(DomainError):
    """Tournament participant operation is invalid."""


class TournamentMatchNotFoundError(DomainError):
    """Tournament match does not exist."""


class TournamentMatchResultError(DomainError):
    """Tournament match result operation is invalid."""


class MatchmakingQueueError(DomainError):
    """Matchmaking queue operation is invalid."""


class MatchRecordValidationError(DomainError):
    """Match record payload is invalid or inconsistent."""
