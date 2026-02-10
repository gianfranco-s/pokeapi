import statistics

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

from src.chart import render_growth_time_histogram
from src.dependencies import BaseUrlDep, CacheDep, CacheTtlDep
from src.models import AllBerryStatsResponse
from src.upstream_api import fetch_berry_data, UpstreamApiError

router = APIRouter()


@router.get("/allBerryStats", response_model=AllBerryStatsResponse)
async def all_berry_stats(
    base_url: BaseUrlDep,
    cache: CacheDep,
    cache_ttl: CacheTtlDep,
) -> AllBerryStatsResponse | JSONResponse:
    try:
        names, growth_times, frequency = await fetch_berry_data(
            base_url, cache, cache_ttl
        )
    except UpstreamApiError:
        return JSONResponse(
            status_code=502,
            content={"detail": "Failed to fetch data from PokeAPI"},
        )

    return AllBerryStatsResponse(
        berries_names=names,
        min_growth_time=min(growth_times),
        max_growth_time=max(growth_times),
        mean_growth_time=statistics.mean(growth_times),
        median_growth_time=statistics.median(growth_times),
        variance_growth_time=statistics.pvariance(growth_times),
        frequency_growth_time=dict(frequency),
    )


@router.get("/histogram", response_class=Response)
async def histogram(
    base_url: BaseUrlDep,
    cache: CacheDep,
    cache_ttl: CacheTtlDep,
) -> Response:
    try:
        _, growth_times, frequency = await fetch_berry_data(
            base_url, cache, cache_ttl
        )
    except UpstreamApiError:
        return JSONResponse(
            status_code=502,
            content={"detail": "Failed to fetch data from PokeAPI"},
        )

    png_bytes: bytes = render_growth_time_histogram(frequency)
    return Response(content=png_bytes, media_type="image/png")
