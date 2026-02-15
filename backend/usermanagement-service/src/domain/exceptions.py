from fastapi import status


class AppError(Exception):
    """Base exception class with HTTP metadata."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_type: str = "INTERNAL_ERROR"

    def __init__(self, detail: str = None):
        self.detail = detail or self.__class__.__name__
        super().__init__(self.detail)


class UserAlreadyExistsError(AppError):
    """Raised when a user with the same email or username already exists."""

    status_code = status.HTTP_409_CONFLICT
    error_type = "USER_ALREADY_EXISTS"


class DatabaseError(AppError):
    """Raised when database operations fail."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_type = "DATABASE_ERROR"


class TokenMissingError(AppError):
    """Raised when auth token is missing."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_type = "TOKEN_MISSING"


class TokenInvalidError(AppError):
    """Raised when auth token is invalid."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_type = "TOKEN_INVALID"


class TokenExpiredError(AppError):
    """Raised when auth token is expired."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_type = "TOKEN_EXPIRED"
