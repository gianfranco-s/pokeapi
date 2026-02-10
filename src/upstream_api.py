import httpx

from src.config import Settings
from src.models import Berry, BerryListResponse

settings = Settings()


async def fetch_all_berries() -> list[Berry]:
    """Fetch all berries from PokeAPI, handling pagination."""
    berries: list[Berry] = []
    url: str | None = f"{settings.pokeapi_base_url}/berry/"

    async with httpx.AsyncClient() as client:
        while url is not None:
            response = await client.get(url)
            response.raise_for_status()
            list_response = BerryListResponse(**response.json())

            for item in list_response.results:
                detail_response = await client.get(item.url)
                detail_response.raise_for_status()
                berry = Berry(**detail_response.json())
                berries.append(berry)

            url = list_response.next

    return berries
