"""Dependency injection configuration."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.settings import settings
from src.domain.contracts import PasswordHasher, TokenProvider
from src.domain.services.otp import OtpService
from src.domain.services.password import PasswordService
from src.domain.services.presence import PresenceService
from src.domain.services.token import TokenService
from src.domain.services.user import UserService
from src.infrastructure.event_publisher import RedisEventPublisher

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

_event_publisher = RedisEventPublisher(settings.REDIS_URL)


async def get_db_session() -> AsyncSession:
    """Dependency to get database session."""
    async with async_session_factory() as session:
        yield session


def get_password_service() -> PasswordHasher:
    """Dependency to get password service."""
    return PasswordService()


def get_event_publisher() -> RedisEventPublisher:
    """Dependency to get event publisher."""
    return _event_publisher


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
    event_publisher: RedisEventPublisher = Depends(get_event_publisher),
) -> UserService:
    """Dependency to get user service."""
    password_service = get_password_service()
    token_service = get_token_service()
    otp_service = get_otp_service()
    return UserService(
        session=session,
        password_service=password_service,
        token_service=token_service,
        otp_service=otp_service,
        event_publisher=event_publisher,
    )


def get_token_service() -> TokenProvider:
    """Dependency to get token service."""
    return TokenService(config=settings.jwt_config)


def get_otp_service() -> OtpService:
    """Dependency to get OTP service."""
    return OtpService(redis_url=settings.REDIS_URL)


def get_presence_service() -> PresenceService:
    """Dependency to get online presence service."""
    return PresenceService(
        redis_url=settings.REDIS_URL,
        ttl_seconds=settings.PRESENCE_TTL_SECONDS,
    )
