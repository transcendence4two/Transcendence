import structlog

from shared.logging.context import (
    clear_business_context,
    get_business_context,
    set_business_context,
)


def setup_function():
    structlog.contextvars.clear_contextvars()


def teardown_function():
    structlog.contextvars.clear_contextvars()


def test_set_business_context_binds_standard_and_extra_fields():
    set_business_context(
        action="join_game",
        game_id="game-1",
        tournament_id="tournament-1",
        room_id="room-9",
    )

    context = get_business_context()

    assert context["action"] == "join_game"
    assert context["game_id"] == "game-1"
    assert context["tournament_id"] == "tournament-1"
    assert context["room_id"] == "room-9"


def test_set_business_context_does_not_bind_when_no_values_are_passed():
    set_business_context()
    context = get_business_context()
    assert context == {}


def test_clear_business_context_removes_only_builtin_fields():
    structlog.contextvars.bind_contextvars(
        **{
            "action": "create_match",
            "game_id": "game-2",
            "tournament_id": "tournament-2",
            "custom_key": "custom-value",
        }
    )

    clear_business_context()
    context = get_business_context()

    assert "action" not in context
    assert "game_id" not in context
    assert "tournament_id" not in context
    assert context["custom_key"] == "custom-value"
