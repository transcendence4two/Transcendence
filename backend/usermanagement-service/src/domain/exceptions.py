from dataclasses import dataclass


@dataclass
class DomainError(Exception):
    """Base exception for domain errors."""

    message: str

    def __str__(self):
        return self.message


class UserAlreadyExistsError(DomainError):
    """User with same email or username already exists."""


class DatabaseError(DomainError):
    """Database operation failed."""


class TokenMissingError(DomainError):
    """Auth token is missing."""


class TokenInvalidError(DomainError):
    """Auth token is invalid."""


class TokenExpiredError(DomainError):
    """Auth token is expired."""
