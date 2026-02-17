from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.contracts import UserOperations, UserRegister
from src.domain.schemas.user import UserRegisterRequest
from src.domain.services.commands.get_user_profile import GetUserProfileCommand
from src.domain.services.commands.register_user import RegisterUserCommand
from src.domain.services.password import PasswordService
from src.infrastructure.event_publisher import EventPublisher

EMAIL_WELCOME_CHANNEL = "email:welcome"
EMAIL_OTP_CHANNEL = "email:otp"


class UserService(UserRegister, UserOperations):
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
            EMAIL_WELCOME_CHANNEL,
            {"email": user.email, "username": user.username},
        )
        return user

    async def send_otp_email(self, email: str, otp_code: str) -> None:
        await self.event_publisher.publish(
            EMAIL_OTP_CHANNEL,
            {"email": email, "otp_code": otp_code},
        )

    async def get_user_profile(self, user_id: str):
        command = GetUserProfileCommand(self.session, user_id)
        return await command.execute()
