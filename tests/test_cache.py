from typing import Any
from unittest.mock import Mock, patch

import pytest

from src.cache import CacheBackend, RedisCache, create_cache
from src.upstream_api import fetch_all_berries
from src.models import Berry


class MockCache(CacheBackend):
    """Mock cache for testing."""

    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.get_calls = 0
        self.set_calls = 0

    def get(self, key: str) -> Any | None:
        self.get_calls += 1
        return self.store.get(key)

    def set(self, key: str, value: Any, ttl: int) -> None:
        self.set_calls += 1
        self.store[key] = value

    def delete(self, key: str) -> None:
        self.store.pop(key, None)

    def clear(self) -> None:
        self.store.clear()


class TestCacheBackend:
    def test_mock_cache_get_miss(self) -> None:
        """Mock cache returns None on cache miss."""
        cache = MockCache()
        assert cache.get("nonexistent") is None
        assert cache.get_calls == 1

    def test_mock_cache_get_hit(self) -> None:
        """Mock cache returns value on cache hit."""
        cache = MockCache()
        cache.set("key1", "value1", 60)
        assert cache.get("key1") == "value1"
        assert cache.get_calls == 1
        assert cache.set_calls == 1

    def test_mock_cache_clear(self) -> None:
        """Mock cache clear removes all entries."""
        cache = MockCache()
        cache.set("key1", "value1", 60)
        cache.set("key2", "value2", 60)
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestRedisCacheInit:
    def test_redis_cache_fails_without_redis_module(self) -> None:
        """RedisCache raises AttributeError if redis module is unavailable."""
        with patch("src.cache.redis", None):
            with pytest.raises(AttributeError):
                RedisCache("redis://localhost:6379/0")

    def test_redis_cache_creates_client(self) -> None:
        """RedisCache creates Redis client from URL."""
        mock_redis = Mock()
        mock_client = Mock()
        mock_redis.from_url.return_value = mock_client

        with patch("src.cache.redis", mock_redis):
            cache = RedisCache("redis://localhost:6379/0")
            assert cache.client == mock_client
            mock_redis.from_url.assert_called_once_with("redis://localhost:6379/0")


class TestCreateCache:
    def test_create_cache_returns_none_without_redis_url(self) -> None:
        """create_cache returns None when redis_url is empty or None."""
        assert create_cache("") is None
        assert create_cache(None) is None

    def test_create_cache_creates_redis_cache_with_url(self) -> None:
        """create_cache creates RedisCache when redis_url is provided."""
        mock_redis = Mock()
        mock_client = Mock()
        mock_redis.from_url.return_value = mock_client

        with patch("src.cache.redis", mock_redis):
            cache = create_cache("redis://localhost:6379/0")
            assert isinstance(cache, RedisCache)
            assert cache.client == mock_client

    def test_create_cache_returns_none_on_redis_error(self) -> None:
        """create_cache returns None if Redis initialization fails."""
        with patch("src.cache.RedisCache", side_effect=Exception("Connection failed")):
            cache = create_cache("redis://localhost:6379/0")
            assert cache is None


class TestCachingIntegration:
    @pytest.mark.asyncio
    async def test_fetch_berries_cache_miss(
        self, mock_pokeapi: Any, sample_berries: list[tuple[str, int]]
    ) -> None:
        """fetch_all_berries fetches from API on cache miss."""
        mock_cache = MockCache()

        berries = await fetch_all_berries(
            "https://pokeapi.co/api/v2", cache=mock_cache, cache_ttl_seconds=3600
        )

        assert len(berries) == 5
        assert mock_cache.get_calls == 1
        assert mock_cache.set_calls == 1
        assert "berries:all" in mock_cache.store

    @pytest.mark.asyncio
    async def test_fetch_berries_cache_hit(self, mock_pokeapi: Any) -> None:
        """fetch_all_berries returns cached data on cache hit."""
        mock_cache = MockCache()
        cached_berries = [
            Berry(
                id=1, name="cached-berry", growth_time=10, max_harvest=5, size=20,
                smoothness=25, soil_dryness=15, natural_gift_power=60,
                natural_gift_type={"name": "fire", "url": "http://test.com"},
                firmness={"name": "soft", "url": "http://test.com"},
                flavors=[], item={"name": "test", "url": "http://test.com"},
            )
        ]
        mock_cache.set("berries:all", cached_berries, 3600)

        berries = await fetch_all_berries(
            "https://pokeapi.co/api/v2", cache=mock_cache, cache_ttl_seconds=3600
        )

        assert berries == cached_berries
        assert mock_cache.get_calls == 1
        # set_calls is still 1 from initial setup
        assert mock_cache.set_calls == 1

    @pytest.mark.asyncio
    async def test_fetch_berries_cache_disabled(
        self, mock_pokeapi: Any, sample_berries: list[tuple[str, int]]
    ) -> None:
        """fetch_all_berries skips cache when cache is None (disabled)."""
        berries = await fetch_all_berries(
            "https://pokeapi.co/api/v2", cache=None, cache_ttl_seconds=3600
        )

        assert len(berries) == 5

    @pytest.mark.asyncio
    async def test_fetch_berries_no_cache_instance(
        self, mock_pokeapi: Any, sample_berries: list[tuple[str, int]]
    ) -> None:
        """fetch_all_berries works when cache instance is None."""
        berries = await fetch_all_berries(
            "https://pokeapi.co/api/v2", cache=None, cache_ttl_seconds=3600
        )

        assert len(berries) == 5
