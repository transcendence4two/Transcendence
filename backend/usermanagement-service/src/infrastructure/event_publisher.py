import json
import logging
from abc import ABC, abstractmethod

import redis.asyncio as redis

logger = logging.getLogger(__name__)


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
        logger.info(f"RedisEventPublisher initialized with URL: {redis_url}")

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            logger.info(f"Connecting to Redis at: {self.redis_url}")
            self._client = redis.from_url(self.redis_url)
            logger.info("Redis client connected successfully")
        return self._client

    async def publish(self, channel: str, event: dict) -> None:
        try:
            logger.info(f"Publishing event to channel '{channel}': {event}")
            client = await self._get_client()
            result = await client.publish(channel, json.dumps(event))
            logger.info(f"Event published successfully. Subscribers notified: {result}")
        except Exception as e:
            logger.error(
                f"Failed to publish event to channel '{channel}': {e}", exc_info=True
            )

    async def close(self) -> None:
        if self._client:
            await self._client.close()
