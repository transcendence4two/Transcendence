from fastapi import status


class AppException(Exception):
    """Base exception class with HTTP metadata."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_type: str = "INTERNAL_ERROR"

    def __init__(self, detail: str = None):
        self.detail = detail or self.__class__.__name__
        super().__init__(self.detail)


class UserAlreadyExistsException(AppException):
    """Raised when a user with the same email or username already exists."""

    status_code = status.HTTP_409_CONFLICT
    error_type = "USER_ALREADY_EXISTS"


class DatabaseException(AppException):
    """Raised when database operations fail."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_type = "DATABASE_ERROR"
