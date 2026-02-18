import secrets

import redis.asyncio as redis


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

    async def verify_otp(self, user_id: str, otp: str) -> bool:
        """Verify OTP against stored value"""
        client = await self._get_client()
        key = f"otp:{user_id}"
        stored_otp = await client.get(key)
        
        if stored_otp is None:
            return False
        
        await client.delete(key)
        
        return stored_otp.decode("utf-8") == otp

    async def close(self) -> None:
        """Close Redis connection"""
        if self._client is not None:
            await self._client.close()
