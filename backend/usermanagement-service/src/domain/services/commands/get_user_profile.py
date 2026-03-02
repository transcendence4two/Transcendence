from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import UserNotFoundError
from src.domain.models.user import User
from src.domain.services.commands.base import Command


class GetUserProfileCommand(Command):
    """Command to get a user profile by ID."""

    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def execute(self) -> User:
        stmt = select(User).where(User.id == self.user_id)
        result = await self.session.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise UserNotFoundError(f"User with id '{self.user_id}' not found")

        return user
