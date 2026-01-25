from abc import ABC, abstractmethod
from src.domain.schemas.user import UserRegisterRequest
from src.domain.models.user import User

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