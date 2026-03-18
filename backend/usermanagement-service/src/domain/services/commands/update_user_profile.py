import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.contracts import PasswordHasher
from src.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.domain.models.user import User
from src.domain.schemas.user import UserProfileUpdateRequest
from src.domain.services.commands.base import Command

logger = structlog.get_logger()


class UpdateUserProfileCommand(Command):
    """Command to update a user profile."""

    def __init__(
        self,
        session: AsyncSession,
        user_id: str,
        payload: UserProfileUpdateRequest,
        password_service: PasswordHasher,
    ):
        self.session = session
        self.user_id = user_id
        self.payload = payload
        self.password_service = password_service

    async def execute(self) -> User:
        user = await self._get_user()

        updated_fields = []

        if self.payload.username:
            await self._ensure_username_unique(self.payload.username)
            user.username = self.payload.username
            updated_fields.append("username")

        if self.payload.email:
            await self._ensure_email_unique(self.payload.email)
            user.email = self.payload.email
            updated_fields.append("email")

        if self.payload.password:
            user.hashed_password = self.password_service.hash_password(
                self.payload.password
            )
            updated_fields.append("password")

        if self.payload.enable_2fa is not None:
            user.enable_2fa = self.payload.enable_2fa
            updated_fields.append("enable_2fa")

        updated_user = await self._persist(user)

        logger.info(
            "User profile updated",
            user_id=self.user_id,
            updated_fields=updated_fields,
        )

        return updated_user

    async def _get_user(self) -> User:
        stmt = select(User).where(User.id == self.user_id)
        result = await self.session.execute(stmt)
        user = result.scalars().first()

        if not user:
            logger.warning("User not found for profile update", user_id=self.user_id)
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
