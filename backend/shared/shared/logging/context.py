import structlog


def set_business_context(
    action: str = None, game_id: str = None, tournament_id: str = None, **extra
):
    """
    Helper para adicionar contexto de negócio aos logs.
    Use dentro das suas rotas/controllers.

    Exemplo:
        set_business_context(action="join_game", game_id="123")
        logger.info("Player joining game")  # Já inclui action e game_id
    """

    context = {}

    if action:
        context["action"] = action
    if game_id:
        context["game_id"] = game_id
    if tournament_id:
        context["tournament_id"] = tournament_id

    context.update(extra)

    if context:
        structlog.contextvars.bind_contextvars(**context)


def get_business_context():
    return structlog.contextvars.get_contextvars()


def clear_business_context():
    business_fields = ["action", "game_id", "tournament_id"]
    current = structlog.contextvars.get_contextvars()

    for field in business_fields:
        if field in current:
            structlog.contextvars.unbind_contextvars(field)
