"""Dependency injection configuration."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.settings import settings
from src.domain.contracts import PasswordHasher, UserRegister
from src.domain.services.password import PasswordService
from src.domain.services.user import UserService
from src.infrastructure.emails_service_client import EmailsServiceClient

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db_session() -> AsyncSession:
    """Dependency to get database session."""
    async with async_session_factory() as session:
        yield session


def get_password_service() -> PasswordHasher:
    """Dependency to get password service."""
    return PasswordService()


def get_emails_service_client() -> EmailsServiceClient:
    """Dependency to get emails-service client."""
    return EmailsServiceClient(base_url=settings.EMAILS_SERVICE_URL)


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserRegister:
    """Dependency to get user service."""
    password_service = get_password_service()
    emails_client = get_emails_service_client()
    return UserService(
        session=session,
        password_service=password_service,
        emails_service_client=emails_client,
    )
