from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.domain.contracts import TournamentManager
from src.domain.models import Base
from src.domain.services.tournament import TournamentService

test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
    connect_args={"check_same_thread": False},
)

test_async_session_factory = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_test_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session_factory() as session:
        yield session


async def get_test_tournament_service(session: AsyncSession) -> TournamentManager:
    return TournamentService(session=session)


async def init_test_database() -> None:
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def cleanup_test_database() -> None:
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
