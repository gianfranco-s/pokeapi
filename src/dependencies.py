from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request

from src.cache import CacheBackend
from src.config import Settings


@lru_cache
def get_settings() -> Settings:
    """Singleton Settings provider. lru_cache ensures one instance per process."""
    return Settings()


def get_base_url(settings: Settings = Depends(get_settings)) -> str:
    """Provide the upstream PokeAPI base URL."""
    return settings.pokeapi_base_url


def get_cache(request: Request) -> CacheBackend | None:
    """Read cache backend from app.state. Returns None when caching is disabled."""
    settings = get_settings()
    if not settings.cache_enabled:
        return None
    return getattr(request.app.state, "cache", None)


def get_cache_ttl(settings: Settings = Depends(get_settings)) -> int:
    """Provide the cache TTL in seconds."""
    return settings.cache_ttl_seconds


BaseUrlDep = Annotated[str, Depends(get_base_url)]
CacheDep = Annotated[CacheBackend | None, Depends(get_cache)]
CacheTtlDep = Annotated[int, Depends(get_cache_ttl)]
