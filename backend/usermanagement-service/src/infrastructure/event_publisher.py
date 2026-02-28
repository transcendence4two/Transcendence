import json
from abc import ABC, abstractmethod

import redis.asyncio as redis
import structlog

logger = structlog.get_logger()


class EventPublisher(ABC):
    """Abstract event publisher contract"""

    @abstractmethod
    async def publish(self, channel: str, event: dict) -> None:
        raise NotImplementedError


class RedisEventPublisher(EventPublisher):
    """Redis implementation of event publisher"""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client: redis.Redis | None = None
        logger.info("RedisEventPublisher initialized")

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            logger.info("Connecting to Redis")
            self._client = redis.from_url(self.redis_url)
            logger.info("Redis client connected successfully")
        return self._client

    async def publish(self, channel: str, event: dict) -> None:
        try:
            client = await self._get_client()
            result = await client.publish(channel, json.dumps(event))
            logger.info(
                "Event published successfully",
                channel=channel,
                subscribers_notified=result,
            )
        except Exception:
            logger.exception("Failed to publish event", channel=channel)

    async def close(self) -> None:
        if self._client:
            await self._client.close()
