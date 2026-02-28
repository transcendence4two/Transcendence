from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.settings import settings
from src.domain.contracts import TournamentManager
from src.domain.services.tournament import TournamentService


def _build_engine_connect_args() -> dict:
    if settings.database_url.startswith("sqlite"):
        return {"timeout": 30}
    return {}


engine = create_async_engine(
    settings.database_url,
    echo=False,
    connect_args=_build_engine_connect_args(),
)
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def get_tournament_service(
    session: AsyncSession = Depends(get_db_session),
) -> TournamentManager:
    return TournamentService(session=session)
