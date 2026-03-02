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


class UserNotFoundError(DomainError):
    """User not found."""


class UnauthorizedActionError(DomainError):
    """User not authorized to perform this action."""


class InvalidCredentialsError(DomainError):
    """Invalid email or password."""


class InvalidOtpError(DomainError):
    """OTP code is invalid or expired."""
