import json
from abc import ABC, abstractmethod

import redis.asyncio as redis


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

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url)
        return self._client

    async def publish(self, channel: str, event: dict) -> None:
        client = await self._get_client()
        await client.publish(channel, json.dumps(event))

    async def close(self) -> None:
        if self._client:
            await self._client.close()
