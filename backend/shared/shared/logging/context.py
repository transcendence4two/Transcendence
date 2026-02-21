import structlog


def set_business_context(
    action: str = None, game_id: str = None, tournament_id: str = None, **extra
):
    """
    Add business/domain context to request logs.

    Use this inside routes/controllers so all subsequent logs in the same request
    include these fields.

    Example:
        set_business_context(action="join_game", game_id="123")
        logger.info("Player joining game")  # Includes action + game_id

    Example-only fields (current placeholders):
    - `game_id`
    - `tournament_id`

    These fields exist as practical examples for future services (e.g. game service,
    tournament service). If your service is not using them yet, you can ignore them
    and pass your own keys with `**extra` (e.g. `order_id`, `room_id`, `match_id`).
    """

    context = {}

    # Common high-level business action, independent of a specific service.
    if action:
        context["action"] = action
    # Domain-specific examples (not mandatory for all services).
    if game_id:
        context["game_id"] = game_id
    if tournament_id:
        context["tournament_id"] = tournament_id

    # Service-specific business keys.
    context.update(extra)

    if context:
        structlog.contextvars.bind_contextvars(**context)


def get_business_context():
    """Return all currently bound context variables for the active request."""
    return structlog.contextvars.get_contextvars()


def clear_business_context():
    """
    Remove only the built-in example business fields from contextvars.

    Note:
    Custom keys passed through `**extra` are not removed here automatically.
    Clear them explicitly with `structlog.contextvars.unbind_contextvars(...)`
    if needed.
    """
    business_fields = ["action", "game_id", "tournament_id"]
    current = structlog.contextvars.get_contextvars()

    for field in business_fields:
        if field in current:
            structlog.contextvars.unbind_contextvars(field)
