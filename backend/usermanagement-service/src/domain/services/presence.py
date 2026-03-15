from datetime import UTC, datetime

import redis.asyncio as redis
import structlog

logger = structlog.get_logger()


class PresenceService:
    """Tracks user online presence using Redis TTL heartbeats."""

    def __init__(self, redis_url: str, ttl_seconds: int = 70):
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds
        self._client: redis.Redis | None = None

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url)
            logger.info("Presence Redis client connected")
        return self._client

    @staticmethod
    def _presence_key(user_id: str) -> str:
        return f"presence:{user_id}"

    async def heartbeat(self, user_id: str) -> None:
        client = await self._get_client()
        now = datetime.now(UTC).isoformat()
        await client.setex(self._presence_key(user_id), self.ttl_seconds, now)

    async def is_online(self, user_id: str) -> bool:
        client = await self._get_client()
        return await client.exists(self._presence_key(user_id)) == 1

    async def set_offline(self, user_id: str) -> None:
        client = await self._get_client()
        await client.delete(self._presence_key(user_id))

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
