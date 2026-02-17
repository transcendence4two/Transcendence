from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.contracts import UserOperations, UserRegister
from src.domain.schemas.user import UserProfileUpdateRequest, UserRegisterRequest
from src.domain.services.commands.get_user_profile import GetUserProfileCommand
from src.domain.services.commands.register_user import RegisterUserCommand
from src.domain.services.commands.toggle_2fa import Toggle2FACommand
from src.domain.services.commands.update_user_profile import UpdateUserProfileCommand
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
        await self.send_welcome_email(user.email, user.username)
        return user

    async def get_user_profile(self, user_id: str):
        command = GetUserProfileCommand(self.session, user_id)
        return await command.execute()

    async def update_user_profile(
        self, user_id: str, payload: UserProfileUpdateRequest
    ):
        command = UpdateUserProfileCommand(self.session, user_id, payload)
        return await command.execute()

    async def toggle_2fa(self, user_id: str, enable: bool):
        command = Toggle2FACommand(self.session, user_id, enable)
        return await command.execute()

    # Messaging methods
    async def send_welcome_email(self, email: str, username: str) -> None:
        await self.event_publisher.publish(
            EMAIL_WELCOME_CHANNEL,
            {"email": email, "username": username},
        )

    async def send_otp_email(self, email: str, otp_code: str) -> None:
        await self.event_publisher.publish(
            EMAIL_OTP_CHANNEL,
            {"email": email, "otp_code": otp_code},
        )
