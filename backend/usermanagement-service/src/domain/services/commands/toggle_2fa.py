import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import UserNotFoundError
from src.domain.models.user import User
from src.domain.services.commands.base import Command

logger = logging.getLogger(__name__)


class Toggle2FACommand(Command):
    """Command to toggle 2FA for a user."""

    def __init__(self, session: AsyncSession, user_id: str, enable: bool):
        self.session = session
        self.user_id = user_id
        self.enable = enable

    async def execute(self) -> User:
        stmt = select(User).where(User.id == self.user_id)
        result = await self.session.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise UserNotFoundError(f"User with id '{self.user_id}' not found")

        user.enable_2fa = self.enable
        updated_user = await self._persist(user)
        logger.info(f"User 2FA toggled: {updated_user.id} - enabled: {self.enable}")
        return updated_user
