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


# Mock Classes for Unit Tests
class MockPasswordService:
    """Mock password service for unit tests"""

    def hash_password(self, password: str) -> str:
        return f"hashed_{password}"


class MockEventPublisher:
    """Mock event publisher for unit tests"""

    def __init__(self):
        self.published_events = []

    async def publish(self, channel: str, data: dict):
        self.published_events.append({"channel": channel, "data": data})


class MockResult:
    """Mock result from database query"""

    def __init__(self, user):
        self.user = user

    def scalars(self):
        return self

    def first(self):
        return self.user


class MockCountResult:
    """Mock result for count query"""

    def __init__(self, count):
        self.count = count

    def scalar(self):
        return self.count


class MockUsersResult:
    """Mock result for users query"""

    def __init__(self, users):
        self.users = users

    def scalars(self):
        return self

    def all(self):
        return self.users


class MockSession:
    def __init__(
        self,
        user_to_return=None,
        users_to_return=None,
        total_count=0,
        conflicting_user=None,
    ):
        self.user_to_return = user_to_return
        self.users_to_return = users_to_return
        self.total_count = total_count
        self.conflicting_user = conflicting_user
        self.executed_stmts = []
        self.added_entities = []
        self.committed = False
        self.query_count = 0
        self._is_pagination = users_to_return is not None

    async def execute(self, stmt):
        self.executed_stmts.append(stmt)
        self.query_count += 1

        # For pagination: first query is count, second is users
        if self._is_pagination:
            if self.query_count == 1:
                return MockCountResult(self.total_count)
            return MockUsersResult(self.users_to_return)

        # For conflict checking: first query is user, second is conflicting user
        if self.query_count == 1:
            return MockResult(self.user_to_return)
        return MockResult(self.conflicting_user)

    def add(self, entity):
        self.added_entities.append(entity)

    async def commit(self):
        self.committed = True

    async def refresh(self, entity):
        pass


# Mock Fixtures
@pytest.fixture
def mock_password_service():
    return MockPasswordService()


@pytest.fixture
def mock_event_publisher():
    return MockEventPublisher()


@pytest.fixture
def mock_session():
    def _mock_session(**kwargs):
        return MockSession(**kwargs)

    return _mock_session
