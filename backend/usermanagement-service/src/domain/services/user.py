from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.contracts import UserRegister
from src.domain.schemas.user import UserRegisterRequest
from src.domain.services.commands.register_user import RegisterUserCommand
from src.domain.services.password import PasswordService
from src.infrastructure.event_publisher import EventPublisher

USER_REGISTERED_CHANNEL = "user:registered"


class UserService(UserRegister):
    """Service for user operations"""

    def __init__(
        self,
        session: AsyncSession,
        password_service: PasswordService,
        event_publisher: EventPublisher,
    ):
        self.session = session
        self.password_service = password_service
        self.event_publisher = event_publisher

    async def register_user(self, payload: UserRegisterRequest):
        command = RegisterUserCommand(
            session=self.session,
            password_service=self.password_service,
            payload=payload,
        )
        user = await command.execute()
        await self.event_publisher.publish(
            USER_REGISTERED_CHANNEL,
            {"email": user.email, "username": user.username},
        )
        return user
