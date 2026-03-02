import secrets

import redis.asyncio as redis
import structlog

logger = structlog.get_logger()


class OtpService:
    """Service for generating and managing One-Time Passwords (OTP)"""

    def __init__(self, redis_url: str, ttl: int = 300):
        """Initialize OTP service"""
        self.redis_url = redis_url
        self.ttl = ttl
        self._client: redis.Redis | None = None

    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client connection"""
        if self._client is None:
            self._client = redis.from_url(self.redis_url)
            logger.info("OTP Redis client connected")
        return self._client

    def generate_otp(self) -> str:
        """Generate a secure 6-digit OTP code"""
        return f"{secrets.randbelow(1000000):06d}"

    async def store_otp(self, user_id: str, otp: str, ttl: int | None = None) -> None:
        """Store OTP in Redis with expiration"""
        client = await self._get_client()
        key = f"otp:{user_id}"
        expiration = ttl if ttl is not None else self.ttl
        await client.setex(key, expiration, otp)
        logger.info("OTP stored in Redis", user_id=user_id, ttl=expiration)

    async def verify_otp(self, user_id: str, otp: str) -> bool:
        """Verify OTP against stored value"""
        client = await self._get_client()
        key = f"otp:{user_id}"
        stored_otp = await client.get(key)

        if stored_otp is None:
            logger.warning("OTP not found or expired", user_id=user_id)
            return False

        if stored_otp.decode("utf-8") == otp:
            await client.delete(key)
            logger.info("OTP verified and consumed", user_id=user_id)
            return True

        logger.warning("OTP mismatch", user_id=user_id)
        return False

    async def close(self) -> None:
        """Close Redis connection"""
        if self._client is not None:
            await self._client.close()
