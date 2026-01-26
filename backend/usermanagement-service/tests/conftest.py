"""Pytest configuration and fixtures for integration tests."""

from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.di_config import get_db_session, get_user_service
from tests.test_di_config import (
    get_test_db_session,
    get_test_user_service,
    init_test_db,
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function", autouse=True)
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    await init_test_db()

    async for session in get_test_db_session():
        yield session
        await session.rollback()


@pytest.fixture
async def app(db_session: AsyncSession) -> FastAPI:
    from main import app as fastapi_app

    async def override_get_db_session():
        yield db_session

    async def override_get_user_service():
        return await get_test_user_service(db_session)

    fastapi_app.dependency_overrides[get_db_session] = override_get_db_session
    fastapi_app.dependency_overrides[get_user_service] = override_get_user_service

    yield fastapi_app

    fastapi_app.dependency_overrides.clear()


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac
