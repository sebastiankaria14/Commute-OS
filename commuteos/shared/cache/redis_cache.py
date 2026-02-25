"""
Redis caching layer for CommuteOS.
Non-blocking async operations with connection pooling.
"""
import json
from typing import Any, Optional
import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool
from ..config.settings import get_settings
from ..utils.logger import get_logger


logger = get_logger(__name__)


class CacheManager:
    """Async Redis cache manager with connection pooling."""
    
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.pool: Optional[ConnectionPool] = None
        self.settings = get_settings()
    
    async def connect(self):
        """Initialize Redis connection with connection pooling."""
        if self.redis_client is not None:
            logger.info("Redis already connected")
            return
        
        logger.info("Initializing Redis connection",
                   host=self.settings.REDIS_HOST,
                   port=self.settings.REDIS_PORT)
        
        self.pool = ConnectionPool.from_url(
            self.settings.redis_url,
            max_connections=self.settings.REDIS_POOL_SIZE,
            decode_responses=True,
        )
        
        self.redis_client = aioredis.Redis(connection_pool=self.pool)
        
        # Test connection
        try:
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client is not None:
            logger.info("Closing Redis connection")
            await self.redis_client.close()
            await self.pool.disconnect()
            self.redis_client = None
            self.pool = None
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if self.redis_client is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        
        try:
            value = await self.redis_client.get(key)
            if value:
                logger.debug("Cache hit", key=key)
                return json.loads(value)
            logger.debug("Cache miss", key=key)
            return None
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return None  # Fail gracefully
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: from settings)
            
        Returns:
            True if successful, False otherwise
        """
        if self.redis_client is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        
        try:
            ttl = ttl or self.settings.CACHE_TTL
            serialized_value = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized_value)
            logger.debug("Cache set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False otherwise
        """
        if self.redis_client is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        
        try:
            result = await self.redis_client.delete(key)
            logger.debug("Cache delete", key=key, deleted=bool(result))
            return bool(result)
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False
    
    async def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful, False otherwise
        """
        if self.redis_client is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        
        try:
            await self.redis_client.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error("Cache clear error", error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        if self.redis_client is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error("Cache exists error", key=key, error=str(e))
            return False


# Global cache manager instance
cache_manager = CacheManager()


def get_cache() -> CacheManager:
    """Get the global cache manager instance."""
    return cache_manager
