import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import InvalidDeleteConfirmationError, UserNotFoundError
from src.domain.models.user import User
from src.domain.services.commands.base import Command

logger = structlog.get_logger()

REQUIRED_DELETE_CONFIRMATION = "Yes, delete my user"


class DeleteUserProfileCommand(Command):
    """Command to delete a user profile with explicit confirmation."""

    def __init__(self, session: AsyncSession, user_id: str, confirmation_text: str):
        self.session = session
        self.user_id = user_id
        self.confirmation_text = confirmation_text

    async def execute(self) -> None:
        self._validate_confirmation_phrase()
        user = await self._get_user()

        await self.session.delete(user)
        await self.session.commit()

        logger.info("User profile deleted", user_id=self.user_id)

    def _validate_confirmation_phrase(self) -> None:
        if self.confirmation_text != REQUIRED_DELETE_CONFIRMATION:
            raise InvalidDeleteConfirmationError(
                f"Invalid confirmation text. Required: '{REQUIRED_DELETE_CONFIRMATION}'"
            )

    async def _get_user(self) -> User:
        stmt = select(User).where(User.id == self.user_id)
        result = await self.session.execute(stmt)
        user = result.scalars().first()

        if not user:
            logger.warning("User not found for deletion", user_id=self.user_id)
            raise UserNotFoundError(f"User with id '{self.user_id}' not found")

        return user
