"""Dependency injection configuration for tests."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.domain.contracts import PasswordHasher, UserRegister
from src.domain.models.user import Base
from src.domain.services.password import PasswordService
from src.domain.services.user import UserService
from src.infrastructure.event_publisher import EventPublisher


class MockEventPublisher(EventPublisher):
    """Mock event publisher for testing"""

    def __init__(self):
        self.published_events: list[tuple[str, dict]] = []

    async def publish(self, channel: str, event: dict) -> None:
        self.published_events.append((channel, event))


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


def get_test_event_publisher() -> MockEventPublisher:
    return MockEventPublisher()


async def get_test_user_service(session: AsyncSession) -> UserRegister:
    password_service = get_test_password_service()
    event_publisher = get_test_event_publisher()
    return UserService(
        session=session,
        password_service=password_service,
        event_publisher=event_publisher,
    )


async def init_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def cleanup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
