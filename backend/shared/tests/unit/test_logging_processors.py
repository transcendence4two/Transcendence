import structlog

from shared.logging.processors import (
    add_request_context,
    add_service,
    rename_event_key,
    rename_level_key,
)


def setup_function():
    structlog.contextvars.clear_contextvars()


def teardown_function():
    structlog.contextvars.clear_contextvars()


def test_add_service_injects_service_name():
    processor = add_service("usermanagement-service")
    event_dict = {"event": "request_received"}

    result = processor(None, None, event_dict)

    assert result["service.name"] == "usermanagement-service"


def test_add_request_context_injects_only_known_request_fields():
    structlog.contextvars.bind_contextvars(
        **{
            "http.request.id": "req-123",
            "trace.id": "trace-456",
            "user.id": "user-1",
            "http.request.method": "GET",
            "url.path": "/health",
            "client.address": "127.0.0.1",
            "user_agent.original": "pytest-agent",
            "unknown.field": "should-not-be-copied",
        }
    )

    result = add_request_context(None, None, {"event": "request_received"})

    assert result["http.request.id"] == "req-123"
    assert result["trace.id"] == "trace-456"
    assert result["user.id"] == "user-1"
    assert result["http.request.method"] == "GET"
    assert result["url.path"] == "/health"
    assert result["client.address"] == "127.0.0.1"
    assert result["user_agent.original"] == "pytest-agent"
    assert "unknown.field" not in result


def test_rename_level_key_renames_level_to_log_level():
    result = rename_level_key(None, None, {"level": "info", "event": "x"})

    assert "level" not in result
    assert result["log.level"] == "info"


def test_rename_event_key_renames_event_to_message():
    result = rename_event_key(None, None, {"event": "request_completed", "x": 1})

    assert "event" not in result
    assert result["message"] == "request_completed"
