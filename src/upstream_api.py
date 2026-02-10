import httpx

from src.config import Settings
from src.models import Berry, BerryListResponse

settings = Settings()


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
