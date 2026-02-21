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
