import structlog

import httpx

from src.domain.contracts import GameServiceClient

logger = structlog.get_logger()


class HTTPGameServiceClient(GameServiceClient):
    """HTTP client for creating game sessions via game-service REST API."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def create_session(
        self,
        player1_user_id: str,
        player2_user_id: str,
    ) -> str:
        url = f"{self._base_url}/api/sessions"
        payload = {
            "tournament_id": "",
            "match_id": "",
            "players": [
                {"user_id": player1_user_id, "participant_id": ""},
                {"user_id": player2_user_id, "participant_id": ""},
            ],
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        session_id = data["session_id"]
        logger.info(
            "Game session created",
            session_id=session_id,
            player1_user_id=player1_user_id,
            player2_user_id=player2_user_id,
        )
        return session_id
