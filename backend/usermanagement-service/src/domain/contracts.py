from abc import ABC, abstractmethod

from src.domain.models.user import User
from src.domain.schemas.user import UserProfileUpdateRequest, UserRegisterRequest


class PasswordHasher(ABC):
    """Port for password hashing/verification."""

    @abstractmethod
    def hash_password(self, password: str) -> str: ...

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...


class UserRegister(ABC):
    """Port for user registration use case."""

    @abstractmethod
    async def register_user(self, payload: UserRegisterRequest) -> User: ...


class UserOperations(ABC):
    """Port for user operations use cases."""

    @abstractmethod
    async def get_user_profile(self, user_id: str) -> User: ...

    @abstractmethod
    async def get_paginated_user_profiles(self, page: int, page_size: int) -> dict: ...

    @abstractmethod
    async def update_user_profile(
        self, user_id: str, payload: UserProfileUpdateRequest
    ) -> User: ...


class TokenProvider(ABC):
    """Port for token operations."""

    @abstractmethod
    def create_token(self, subject: str, expires_minutes: int | None = None) -> str: ...

    @abstractmethod
    def validate_token(self, token: str) -> dict: ...


class UserRepository(ABC):
    """Port for user data access."""

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None: ...


class EventPublisher(ABC):
    """Port for event publishing."""

    @abstractmethod
    async def publish(self, channel: str, data: dict) -> None: ...
