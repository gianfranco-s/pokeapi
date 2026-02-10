import statistics
from collections import Counter

import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

from src.chart import render_growth_time_histogram
from src.models import AllBerryStatsResponse
from src.upstream_api import fetch_all_berries
from src.config import Settings

router = APIRouter()
upstream_url = Settings().pokeapi_base_url

@router.get("/allBerryStats", response_model=AllBerryStatsResponse)
async def all_berry_stats() -> AllBerryStatsResponse | JSONResponse:
    try:
        berries = await fetch_all_berries(upstream_url)
    except httpx.HTTPError:
        return JSONResponse(
            status_code=502,
            content={"detail": "Failed to fetch data from PokeAPI"},
        )

    growth_times: list[int] = [b.growth_time for b in berries]
    freq: Counter[int] = Counter(growth_times)

    return AllBerryStatsResponse(
        berries_names=[b.name for b in berries],
        min_growth_time=min(growth_times),
        max_growth_time=max(growth_times),
        mean_growth_time=statistics.mean(growth_times),
        median_growth_time=statistics.median(growth_times),
        variance_growth_time=statistics.pvariance(growth_times),
        frequency_growth_time=dict(freq),
    )


@router.get("/histogram", response_class=Response)
async def histogram() -> Response:
    try:
        berries = await fetch_all_berries(upstream_url)
    except httpx.HTTPError:
        return JSONResponse(
            status_code=502,
            content={"detail": "Failed to fetch data from PokeAPI"},
        )

    growth_times: list[int] = [b.growth_time for b in berries]
    freq: Counter[int] = Counter(growth_times)
    png_bytes: bytes = render_growth_time_histogram(freq)

    return Response(content=png_bytes, media_type="image/png")
