import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.domain.models.user import User
from src.domain.schemas.user import UserProfileUpdateRequest
from src.domain.services.commands.base import Command

logger = logging.getLogger(__name__)


class UpdateUserProfileCommand(Command):
    """Command to update a user profile."""

    def __init__(
        self,
        session: AsyncSession,
        user_id: str,
        payload: UserProfileUpdateRequest,
    ):
        self.session = session
        self.user_id = user_id
        self.payload = payload

    async def execute(self) -> User:
        user = await self._get_user()

        if self.payload.username:
            await self._ensure_username_unique(self.payload.username)
            user.username = self.payload.username

        if self.payload.email:
            await self._ensure_email_unique(self.payload.email)
            user.email = self.payload.email

        updated_user = await self._persist(user)
        logger.info(f"User profile updated: {updated_user.id}")
        return updated_user

    async def _get_user(self) -> User:
        stmt = select(User).where(User.id == self.user_id)
        result = await self.session.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise UserNotFoundError(f"User with id '{self.user_id}' not found")

        return user

    async def _ensure_username_unique(self, username: str) -> None:
        stmt = select(User).where(User.username == username, User.id != self.user_id)
        result = await self.session.execute(stmt)
        if result.scalars().first():
            raise UserAlreadyExistsError(f"Username '{username}' is already taken")

    async def _ensure_email_unique(self, email: str) -> None:
        stmt = select(User).where(User.email == email, User.id != self.user_id)
        result = await self.session.execute(stmt)
        if result.scalars().first():
            raise UserAlreadyExistsError(f"Email '{email}' is already registered")
