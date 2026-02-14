"""Tests for the Redis event publisher."""

import pytest

from src.infrastructure.event_publisher import EventPublisher


class MockEventPublisher(EventPublisher):
    """Mock event publisher for testing"""

    def __init__(self):
        self.published_events: list[tuple[str, dict]] = []

    async def publish(self, channel: str, event: dict) -> None:
        self.published_events.append((channel, event))


@pytest.fixture
def mock_event_publisher() -> MockEventPublisher:
    return MockEventPublisher()


@pytest.mark.anyio
async def test_mock_event_publisher_publishes_event(
    mock_event_publisher: MockEventPublisher,
):
    """Test that the mock event publisher correctly records published events."""
    channel = "email:welcome"
    event = {"email": "test@example.com", "username": "testuser"}

    await mock_event_publisher.publish(channel, event)

    assert len(mock_event_publisher.published_events) == 1
    assert mock_event_publisher.published_events[0] == (channel, event)


@pytest.mark.anyio
async def test_mock_event_publisher_multiple_events(
    mock_event_publisher: MockEventPublisher,
):
    """Test that multiple events are recorded correctly."""
    events = [
        ("email:welcome", {"email": "user1@example.com", "username": "user1"}),
        ("email:otp", {"email": "user2@example.com", "otp_code": "123456"}),
    ]

    for channel, event in events:
        await mock_event_publisher.publish(channel, event)

    assert len(mock_event_publisher.published_events) == 2
    assert mock_event_publisher.published_events == events
