import logging
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import UserAlreadyExistsError
from src.domain.models.user import User
from src.domain.schemas.user import UserRegisterRequest
from src.domain.services.commands.base import Command
from src.domain.services.password import PasswordService

logger = logging.getLogger(__name__)


class RegisterUserCommand(Command):
    """Command to register a new user."""

    def __init__(
        self,
        session: AsyncSession,
        password_service: PasswordService,
        payload: UserRegisterRequest,
    ):
        self.session = session
        self.password_service = password_service
        self.payload = payload

    async def execute(self) -> User:
        """Execute user registration with validation and error handling"""
        await self._ensure_unique(self.payload.username, self.payload.email)
        user = await self._create_user()
        logger.info(f"User registered successfully: {user.id}")
        return user

    async def _create_user(self) -> User:
        """Create and persist the user"""
        hashed_password = self.password_service.hash_password(self.payload.password)

        user = User(
            id=str(uuid4()),
            username=self.payload.username,
            email=self.payload.email,
            hashed_password=hashed_password,
            enable_2fa=self.payload.enable_2fa,
        )

        return await self._persist(user)

    async def _ensure_unique(self, username: str, email: str) -> None:
        """Check if username and email are unique in a single query."""
        stmt = select(User).where(or_(User.username == username, User.email == email))
        result = await self.session.execute(stmt)
        existing_user = result.scalars().first()

        if existing_user:
            if existing_user.username == username:
                raise UserAlreadyExistsError(f"Username '{username}' is already taken")
            if existing_user.email == email:
                raise UserAlreadyExistsError(f"Email '{email}' is already registered")
