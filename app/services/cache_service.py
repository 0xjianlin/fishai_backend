import hashlib
import json
import time
from typing import Optional, Dict, Any
import redis
import logging
from ..utils.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client = None
        self.ttl = 3600  # 1 hour default TTL
        self._init_redis()

    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
            self.redis_client = None
            self._memory_cache = {}

    def _generate_key(self, image_data: bytes) -> str:
        """Generate a unique key for the image data"""
        return hashlib.sha256(image_data).hexdigest()

    async def get_cached_result(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """Get cached identification result for an image"""
        try:
            key = self._generate_key(image_data)
            
            if self.redis_client:
                # Try Redis first
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
            else:
                # Fallback to memory cache
                if key in self._memory_cache:
                    result, expiry = self._memory_cache[key]
                    if time.time() < expiry:
                        return result
                    else:
                        del self._memory_cache[key]
            
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    async def cache_result(self, image_data: bytes, result: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache identification result for an image"""
        try:
            key = self._generate_key(image_data)
            expiry = ttl or self.ttl
            
            if self.redis_client:
                # Store in Redis
                return self.redis_client.setex(
                    key,
                    expiry,
                    json.dumps(result)
                )
            else:
                # Store in memory
                self._memory_cache[key] = (
                    result,
                    time.time() + expiry
                )
                return True
                
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
            return False

    async def invalidate_cache(self, image_data: bytes) -> bool:
        """Remove cached result for an image"""
        try:
            key = self._generate_key(image_data)
            
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return False

    async def clear_cache(self) -> bool:
        """Clear all cached results"""
        try:
            if self.redis_client:
                return bool(self.redis_client.flushdb())
            else:
                self._memory_cache.clear()
                return True
                
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

# Create singleton instance
cache_service = CacheService() 