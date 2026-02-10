import httpx
from collections import Counter

from src.cache import CacheBackend
from src.models import Berry, BerryListResponse


class UpstreamApiError(Exception):
    """Raised when upstream API (PokeAPI) fails."""
    pass


async def fetch_all_berries(
    base_url: str,
    cache: CacheBackend | None,
    cache_ttl_seconds: int,
    endpoint: str = "berry/",
) -> list[Berry]:
    """Fetch all berries from PokeAPI, handling pagination and caching."""
    cache_key = "berries:all"

    if cache is not None:
        cached_berries = cache.get(cache_key)
        if cached_berries is not None:
            return cached_berries

    berries = await _fetch_all_berries_from_api(base_url, endpoint)

    if cache is not None:
        cache.set(cache_key, berries, cache_ttl_seconds)

    return berries


async def _fetch_all_berries_from_api(base_url: str, endpoint: str = "berry/") -> list[Berry]:
    """Internal function to fetch berries from API without caching."""
    berries: list[Berry] = []
    url = f"{base_url}/{endpoint}"
    MAX_PAGES = 100  # Safety limit to prevent infinite loops

    async with httpx.AsyncClient(timeout=30.0) as client:
        page_count = 0
        while url is not None and page_count < MAX_PAGES:
            response = await client.get(url)
            response.raise_for_status()
            list_response = BerryListResponse(**response.json())

            for item in list_response.results:
                detail_response = await client.get(item.url)
                detail_response.raise_for_status()
                berry = Berry(**detail_response.json())
                berries.append(berry)

            url = list_response.next
            page_count += 1

    return berries


async def fetch_berry_data(
    base_url: str,
    cache: CacheBackend | None,
    cache_ttl_seconds: int,
) -> tuple[list[str], list[int], Counter[int]]:
    """Fetch and process berry data. Returns (names, growth_times, frequency)."""
    try:
        berries = await fetch_all_berries(base_url, cache, cache_ttl_seconds)
    except httpx.HTTPError as e:
        raise UpstreamApiError("Failed to fetch data from PokeAPI") from e

    names = [b.name for b in berries]
    growth_times = [b.growth_time for b in berries]
    frequency = Counter(growth_times)

    return names, growth_times, frequency
