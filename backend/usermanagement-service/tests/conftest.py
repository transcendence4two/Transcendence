"""Pytest configuration and fixtures for integration tests."""

from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.di_config import get_db_session, get_user_service
from src.domain.services.user import UserService
from tests.test_di_config import (
    MockEventPublisher,
    MockOtpService,
    get_test_db_session,
    get_test_password_service,
    get_test_token_service,
    init_test_db,
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
def mock_event_publisher() -> MockEventPublisher:
    """Fixture for mock event publisher that is cleared between tests"""
    publisher = MockEventPublisher()
    yield publisher
    publisher.published_events.clear()


@pytest.fixture(scope="function")
def mock_otp_service() -> MockOtpService:
    """Fixture for mock OTP service that is cleared between tests"""
    otp_service = MockOtpService()
    yield otp_service
    otp_service.stored_otps.clear()


@pytest.fixture(scope="function", autouse=True)
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    await init_test_db()

    async for session in get_test_db_session():
        yield session
        await session.rollback()


@pytest.fixture
async def app(
    db_session: AsyncSession,
    mock_event_publisher: MockEventPublisher,
    mock_otp_service: MockOtpService,
) -> FastAPI:
    from main import app as fastapi_app

    async def override_get_db_session():
        yield db_session

    async def override_get_user_service():
        return UserService(
            session=db_session,
            password_service=get_test_password_service(),
            token_service=get_test_token_service(),
            otp_service=mock_otp_service,
            event_publisher=mock_event_publisher,
        )

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
