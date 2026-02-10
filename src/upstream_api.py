import httpx
from collections import Counter

from src.config import Settings
from src.models import Berry, BerryListResponse

settings = Settings()


class UpstreamApiError(Exception):
    """Raised when upstream API (PokeAPI) fails."""
    pass


async def fetch_all_berries(base_url: str, endpoint: str = "berry/") -> list[Berry]:
    """Fetch all berries from PokeAPI, handling pagination."""
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


async def fetch_berry_data() -> tuple[list[str], list[int], Counter[int]]:
    """Fetch and process berry data. Returns (names, growth_times, frequency)."""
    try:
        berries = await fetch_all_berries(settings.pokeapi_base_url)
    except httpx.HTTPError as e:
        raise UpstreamApiError("Failed to fetch data from PokeAPI") from e
    
    names = [b.name for b in berries]
    growth_times = [b.growth_time for b in berries]
    frequency = Counter(growth_times)
    
    return names, growth_times, frequency


async def fetch_berry_data() -> tuple[list[str], list[int], Counter[int]]:
    """Fetch and process berry data. Returns (names, growth_times, frequency)."""
    try:
        berries = await fetch_all_berries(settings.pokeapi_base_url)
    except httpx.HTTPError as e:
        raise UpstreamApiError("Failed to fetch data from PokeAPI") from e
    
    names = [b.name for b in berries]
    growth_times = [b.growth_time for b in berries]
    frequency = Counter(growth_times)
    
    return names, growth_times, frequency
