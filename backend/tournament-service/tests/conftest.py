from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.di_config import get_db_session, get_tournament_service
from tests.test_di_config import (
    get_test_db_session,
    get_test_tournament_service,
    init_test_database,
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function", autouse=True)
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    await init_test_database()

    async for session in get_test_db_session():
        yield session
        await session.rollback()


@pytest.fixture
async def app(db_session: AsyncSession) -> FastAPI:
    from main import app

    async def override_get_db_session():
        yield db_session

    async def override_get_tournament_service():
        return await get_test_tournament_service(db_session)

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_tournament_service] = (
        override_get_tournament_service
    )

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as async_client:
        yield async_client
