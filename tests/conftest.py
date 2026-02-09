from typing import Any
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


SAMPLE_BERRIES: list[tuple[str, int]] = [
    ("cheri", 3),
    ("chesto", 3),
    ("pecha", 3),
    ("rawst", 4),
    ("aspear", 5),
]


def _make_berry_detail(name: str, growth_time: int) -> dict[str, Any]:
    """Build a minimal PokeAPI berry detail dict."""
    return {
        "id": hash(name) % 1000,
        "name": name,
        "growth_time": growth_time,
        "max_harvest": 5,
        "size": 20,
        "smoothness": 25,
        "soil_dryness": 15,
        "natural_gift_power": 60,
        "firmness": {"name": "soft", "url": "https://pokeapi.co/api/v2/berry-firmness/2/"},
        "flavors": [],
        "item": {"name": f"{name}-berry", "url": f"https://pokeapi.co/api/v2/item/{hash(name) % 1000}/"},
        "natural_gift_type": {"name": "fire", "url": "https://pokeapi.co/api/v2/type/10/"},
    }


def _make_berry_list_response(
    berries: list[tuple[str, int]],
    *,
    offset: int = 0,
    next_url: str | None = None,
) -> dict[str, Any]:
    """Build a PokeAPI paginated berry list response."""
    return {
        "count": len(berries),
        "next": next_url,
        "previous": None,
        "results": [
            {"name": name, "url": f"https://pokeapi.co/api/v2/berry/{i + offset + 1}/"}
            for i, (name, _) in enumerate(berries)
        ],
    }


@pytest.fixture()
def sample_berries() -> list[tuple[str, int]]:
    """Known berries with growth_times [3, 3, 3, 4, 5]."""
    return SAMPLE_BERRIES.copy()


@pytest.fixture()
def mock_berry_list_response() -> dict[str, Any]:
    """Single-page list response for sample berries."""
    return _make_berry_list_response(SAMPLE_BERRIES)


@pytest.fixture()
def mock_berry_detail():
    """Factory that returns a berry detail dict."""
    return _make_berry_detail


@pytest.fixture()
def app() -> Any:
    return create_app()


@pytest.fixture()
def client(app: Any) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def mock_pokeapi(mock_berry_list_response: dict[str, Any]) -> Generator[AsyncMock, None, None]:
    """Patch httpx calls to return mocked PokeAPI responses."""
    berry_details = {name: _make_berry_detail(name, gt) for name, gt in SAMPLE_BERRIES}

    async def mock_get(url: str, **kwargs: Any) -> AsyncMock:
        response = AsyncMock()
        response.raise_for_status = lambda: None

        if "/api/v2/berry/" in url and url.rstrip("/").split("/")[-1].isdigit():
            berry_id = int(url.rstrip("/").split("/")[-1])
            berry_name = SAMPLE_BERRIES[berry_id - 1][0]
            response.json.return_value = berry_details[berry_name]
        else:
            response.json.return_value = mock_berry_list_response

        return response

    with patch("src.router.httpx.AsyncClient") as mock_client_cls:
        mock_client_instance = AsyncMock()
        mock_client_instance.get = mock_get
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client_instance
        yield mock_client_instance


@pytest.fixture()
def mock_pokeapi_paginated() -> Generator[AsyncMock, None, None]:
    """Patch httpx to return two pages of berries."""
    page1_berries = SAMPLE_BERRIES[:3]
    page2_berries = SAMPLE_BERRIES[3:]

    page1 = _make_berry_list_response(
        page1_berries,
        offset=0,
        next_url="https://pokeapi.co/api/v2/berry/?offset=3&limit=3",
    )
    page2 = _make_berry_list_response(page2_berries, offset=3)

    all_details = {name: _make_berry_detail(name, gt) for name, gt in SAMPLE_BERRIES}
    call_count = 0

    async def mock_get(url: str, **kwargs: Any) -> AsyncMock:
        nonlocal call_count
        response = AsyncMock()
        response.raise_for_status = lambda: None

        if "/api/v2/berry/" in url and url.rstrip("/").split("/")[-1].isdigit():
            berry_id = int(url.rstrip("/").split("/")[-1])
            berry_name = SAMPLE_BERRIES[berry_id - 1][0]
            response.json.return_value = all_details[berry_name]
        elif "offset=3" in url:
            response.json.return_value = page2
        else:
            response.json.return_value = page1

        return response

    with patch("src.router.httpx.AsyncClient") as mock_client_cls:
        mock_client_instance = AsyncMock()
        mock_client_instance.get = mock_get
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client_instance
        yield mock_client_instance


@pytest.fixture()
def mock_pokeapi_error() -> Generator[AsyncMock, None, None]:
    """Patch httpx to simulate PokeAPI being unreachable."""
    import httpx

    async def mock_get(url: str, **kwargs: Any) -> None:
        raise httpx.ConnectError("Connection refused")

    with patch("src.router.httpx.AsyncClient") as mock_client_cls:
        mock_client_instance = AsyncMock()
        mock_client_instance.get = mock_get
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client_instance
        yield mock_client_instance
