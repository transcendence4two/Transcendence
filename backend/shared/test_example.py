"""
Example usage of shared-middlewares package.

Shows how to:
- Configure middlewares
- Add business context to logs
- Use structured logging
"""

from fastapi import FastAPI, APIRouter
import structlog
from shared import (
    configure_logging,
    request_context_middleware,
    auth_middleware,
    logging_middleware,
)
from shared.logging.context import set_business_context

# =============================================================================
# 1. SETUP (copy this to your main.py)
# =============================================================================

configure_logging(service_name="your-service-name")  # e.g. "auth", "game", "chat"

app = FastAPI()

# IMPORTANT: middleware order matters!
app.middleware("http")(request_context_middleware())  # 1st: request_id, timing
app.middleware("http")(auth_middleware())  # 2nd: JWT auth (optional)
app.middleware("http")(logging_middleware())  # 3rd: final log (always last!)

# =============================================================================
# 2. ROUTE EXAMPLE (copy this to your routes)
# =============================================================================

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/games/{game_id}/join")
async def join_game(game_id: str, user_id: str):
    # Add business context - ALL logs from this point will include these fields
    set_business_context(action="join_game", game_id=game_id)

    logger.info("Processing join game request")

    try:
        # Your business logic here
        result = await join_player_to_game(game_id, user_id)

        logger.info("player_joined_game", player_count=result.player_count)

        return {"success": True}

    except Exception as e:
        logger.exception("join_game_failed")
        raise


# =============================================================================
# 3. SIMULATED FUNCTION (replace with your actual logic)
# =============================================================================


async def join_player_to_game(game_id: str, user_id: str):
    # Your actual implementation
    return {"player_count": 4}


# =============================================================================
# 4. INCLUDE ROUTER (copy this to your main.py)
# =============================================================================

app.include_router(router)

# =============================================================================
# 5. HEALTH CHECK (copy this to your main.py)
# =============================================================================


@app.get("/health")
async def health():
    return {"status": "ok"}
