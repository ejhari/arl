"""Redis client configuration"""

from redis.asyncio import Redis
from typing import Optional
from app.core.config import settings

redis_client: Optional[Redis] = None


async def get_redis_client() -> Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def close_redis_client():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


class RedisPubSub:
    """Redis Pub/Sub manager for event broadcasting"""

    def __init__(self):
        self.redis: Optional[Redis] = None
        self.pubsub = None

    async def initialize(self):
        """Initialize Redis connection and pubsub"""
        self.redis = await get_redis_client()
        self.pubsub = self.redis.pubsub()

    async def publish(self, channel: str, message: str):
        """Publish message to channel"""
        if self.redis:
            await self.redis.publish(channel, message)

    async def subscribe(self, *channels: str):
        """Subscribe to channels"""
        if self.pubsub:
            await self.pubsub.subscribe(*channels)

    async def unsubscribe(self, *channels: str):
        """Unsubscribe from channels"""
        if self.pubsub:
            await self.pubsub.unsubscribe(*channels)

    async def listen(self):
        """Listen for messages"""
        if self.pubsub:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    yield message

    async def close(self):
        """Close pubsub connection"""
        if self.pubsub:
            await self.pubsub.close()


# Global pubsub instance
pubsub = RedisPubSub()
