from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.contracts import UserRegister
from src.domain.schemas.user import UserRegisterRequest
from src.domain.services.commands.register_user import RegisterUserCommand
from src.domain.services.password import PasswordService


class UserService(UserRegister):
    """Service for user operations"""

    def __init__(self, session: AsyncSession, password_service: PasswordService):
        self.session = session
        self.password_service = password_service

    async def register_user(self, payload: UserRegisterRequest):
        command = RegisterUserCommand(
            session=self.session,
            password_service=self.password_service,
            payload=payload,
        )
        return await command.execute()
