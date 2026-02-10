import pickle
from typing import Any
from abc import ABC, abstractmethod

import redis


class CacheBackend(ABC):
    """Abstract cache backend interface."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in cache with TTL in seconds."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass


class RedisCache(CacheBackend):
    """Redis-based cache with TTL support."""

    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url)

    def get(self, key: str) -> Any | None:
        """Get value from Redis cache, returns None if missing or expired."""
        try:
            data = self.client.get(key)
            if data is None:
                return None
            return pickle.loads(data)
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in Redis cache with TTL in seconds."""
        try:
            serialized = pickle.dumps(value)
            self.client.setex(key, ttl, serialized)
        except Exception:
            pass

    def delete(self, key: str) -> None:
        """Delete key from Redis cache."""
        try:
            self.client.delete(key)
        except Exception:
            pass

    def clear(self) -> None:
        """Clear all cache entries."""
        try:
            self.client.flushdb()
        except Exception:
            pass


def create_cache(redis_url: str | None) -> CacheBackend | None:
    """Factory: create a cache backend from a Redis URL, or None if unavailable."""
    if redis_url is None:
        return None
    try:
        return RedisCache(redis_url)
    except Exception:
        return None
