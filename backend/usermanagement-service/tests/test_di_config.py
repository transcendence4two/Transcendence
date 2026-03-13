"""Dependency injection configuration for tests."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.settings import JWTConfig
from src.domain.contracts import PasswordHasher, TokenProvider, UserRegister
from src.domain.models.user import Base
from src.domain.services.otp import OtpService
from src.domain.services.password import PasswordService
from src.domain.services.token import TokenService
from src.domain.services.user import UserService
from src.infrastructure.event_publisher import EventPublisher


class MockEventPublisher(EventPublisher):
    """Mock event publisher for testing"""

    def __init__(self):
        self.published_events: list[tuple[str, dict]] = []

    async def publish(self, channel: str, event: dict) -> None:
        self.published_events.append((channel, event))


class MockOtpService(OtpService):
    """Mock OTP service for testing"""

    def __init__(self):
        self.stored_otps: dict[str, str] = {}

    async def _get_client(self):
        return None

    def generate_otp(self) -> str:
        return "123456"

    async def store_otp(self, user_id: str, otp: str, ttl: int | None = None) -> None:
        self.stored_otps[user_id] = otp

    async def verify_otp(self, user_id: str, otp: str) -> bool:
        if user_id not in self.stored_otps:
            return False
        stored = self.stored_otps.pop(user_id)
        return stored == otp

    async def close(self) -> None:
        pass


test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
    connect_args={"check_same_thread": False},
)

test_async_session_factory = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_test_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session_factory() as session:
        yield session


def get_test_password_service() -> PasswordHasher:
    return PasswordService()


def get_test_token_service() -> TokenProvider:
    config = JWTConfig(
        secret="test-secret-key-for-testing-purposes-only-32-chars-minimum",
        algorithm="HS256",
        issuer="usermanagement-test",
        expires_minutes=60,
    )
    return TokenService(config)


def get_test_otp_service() -> MockOtpService:
    return MockOtpService()


def get_test_event_publisher() -> MockEventPublisher:
    return MockEventPublisher()


async def get_test_user_service(session: AsyncSession) -> UserRegister:
    password_service = get_test_password_service()
    token_service = get_test_token_service()
    otp_service = get_test_otp_service()
    event_publisher = get_test_event_publisher()
    
    class LocalMockStorageService:
        def upload_avatar(self, bytes_data, name):
            return "http://mock-minio/avatars/file.png"
            
    storage_service = LocalMockStorageService()
    
    return UserService(
        session=session,
        password_service=password_service,
        token_service=token_service,
        otp_service=otp_service,
        event_publisher=event_publisher,
        storage_service=storage_service,
    )


async def init_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def cleanup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
