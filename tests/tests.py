from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.models import AllBerryStatsResponse, Berry, BerryListResponse
from src.config import Settings
from src.main import create_app


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class TestBerryModel:
    def test_berry_model_parses_valid_data(self, mock_berry_detail: Any) -> None:
        """Berry model accepts a valid PokeAPI berry dict."""
        data = mock_berry_detail("cheri", 3)
        berry = Berry(**data)
        assert berry.name == "cheri"
        assert berry.growth_time == 3

    def test_berry_list_response_parses_paginated_data(
        self, mock_berry_list_response: dict[str, Any]
    ) -> None:
        """BerryListResponse parses list endpoint with count, next, results."""
        response = BerryListResponse(**mock_berry_list_response)
        assert response.count == 5
        assert response.next is None
        assert len(response.results) == 5

    def test_all_berry_stats_response_schema(self) -> None:
        """AllBerryStatsResponse serializes with all required fields."""
        stats = AllBerryStatsResponse(
            berries_names=["cheri", "chesto"],
            min_growth_time=2,
            median_growth_time=3.0,
            max_growth_time=4,
            variance_growth_time=1.0,
            mean_growth_time=3.0,
            frequency_growth_time={2: 1, 4: 1},
        )
        data = stats.model_dump()
        assert "berries_names" in data
        assert "min_growth_time" in data
        assert "median_growth_time" in data
        assert "max_growth_time" in data
        assert "variance_growth_time" in data
        assert "mean_growth_time" in data
        assert "frequency_growth_time" in data


# ---------------------------------------------------------------------------
# GET /allBerryStats
# ---------------------------------------------------------------------------

class TestAllBerryStats:
    def test_all_berry_stats_returns_200(
        self, client: TestClient, mock_pokeapi: Any
    ) -> None:
        response = client.get("/allBerryStats")
        assert response.status_code == 200

    def test_all_berry_stats_response_has_all_fields(
        self, client: TestClient, mock_pokeapi: Any
    ) -> None:
        response = client.get("/allBerryStats")
        data = response.json()
        expected_keys = {
            "berries_names",
            "min_growth_time",
            "median_growth_time",
            "max_growth_time",
            "variance_growth_time",
            "mean_growth_time",
            "frequency_growth_time",
        }
        assert expected_keys == set(data.keys())

    def test_all_berry_stats_berries_names(
        self, client: TestClient, mock_pokeapi: Any, sample_berries: list[tuple[str, int]]
    ) -> None:
        response = client.get("/allBerryStats")
        data = response.json()
        expected_names = sorted(name for name, _ in sample_berries)
        assert sorted(data["berries_names"]) == expected_names

    def test_all_berry_stats_min_growth_time(
        self, client: TestClient, mock_pokeapi: Any
    ) -> None:
        """min of [3, 3, 3, 4, 5] = 3"""
        response = client.get("/allBerryStats")
        assert response.json()["min_growth_time"] == 3

    def test_all_berry_stats_max_growth_time(
        self, client: TestClient, mock_pokeapi: Any
    ) -> None:
        """max of [3, 3, 3, 4, 5] = 5"""
        response = client.get("/allBerryStats")
        assert response.json()["max_growth_time"] == 5

    def test_all_berry_stats_mean_growth_time(
        self, client: TestClient, mock_pokeapi: Any
    ) -> None:
        """mean of [3, 3, 3, 4, 5] = 3.6"""
        response = client.get("/allBerryStats")
        assert response.json()["mean_growth_time"] == pytest.approx(3.6)

    def test_all_berry_stats_median_growth_time(
        self, client: TestClient, mock_pokeapi: Any
    ) -> None:
        """median of [3, 3, 3, 4, 5] = 3.0"""
        response = client.get("/allBerryStats")
        assert response.json()["median_growth_time"] == pytest.approx(3.0)

    def test_all_berry_stats_variance_growth_time(
        self, client: TestClient, mock_pokeapi: Any
    ) -> None:
        """population variance of [3, 3, 3, 4, 5] = 0.64"""
        response = client.get("/allBerryStats")
        assert response.json()["variance_growth_time"] == pytest.approx(0.64)

    def test_all_berry_stats_frequency_growth_time(
        self, client: TestClient, mock_pokeapi: Any
    ) -> None:
        """frequency of [3, 3, 3, 4, 5] = {3: 3, 4: 1, 5: 1}"""
        response = client.get("/allBerryStats")
        freq = response.json()["frequency_growth_time"]
        # JSON keys are strings
        assert freq == {"3": 3, "4": 1, "5": 1}

    def test_all_berry_stats_handles_pagination(
        self, client: TestClient, mock_pokeapi_paginated: Any, sample_berries: list[tuple[str, int]]
    ) -> None:
        """Mocks two pages of results, verifies all berries appear."""
        response = client.get("/allBerryStats")
        data = response.json()
        expected_names = sorted(name for name, _ in sample_berries)
        assert sorted(data["berries_names"]) == expected_names

    def test_all_berry_stats_pokeapi_error_returns_error_response(
        self, client: TestClient, mock_pokeapi_error: Any
    ) -> None:
        """When PokeAPI is unreachable, returns an error status."""
        response = client.get("/allBerryStats")
        assert response.status_code >= 500


# ---------------------------------------------------------------------------
# GET /histogram
# ---------------------------------------------------------------------------

class TestHistogram:
    def test_histogram_returns_200(
        self, client: TestClient, mock_pokeapi: Any
    ) -> None:
        response = client.get("/histogram")
        assert response.status_code == 200

    def test_histogram_returns_image_content_type(
        self, client: TestClient, mock_pokeapi: Any
    ) -> None:
        response = client.get("/histogram")
        assert "image/png" in response.headers["content-type"]

    def test_histogram_returns_valid_image_bytes(
        self, client: TestClient, mock_pokeapi: Any
    ) -> None:
        response = client.get("/histogram")
        # PNG files start with the magic bytes \x89PNG
        assert response.content[:4] == b"\x89PNG"


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

class TestAppFactory:
    def test_create_app_returns_fastapi_instance(self) -> None:
        app = create_app()
        assert isinstance(app, FastAPI)

    def test_routes_registered(self) -> None:
        app = create_app()
        route_paths = [route.path for route in app.routes]
        assert "/allBerryStats" in route_paths
        assert "/histogram" in route_paths


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

class TestConfig:
    def test_config_loads_defaults(self) -> None:
        """Settings loads with sensible defaults when no env vars set."""
        settings = Settings()
        assert settings.pokeapi_base_url is not None
        assert len(settings.pokeapi_base_url) > 0

    def test_config_overrides_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings picks up env var overrides."""
        monkeypatch.setenv("POKEAPI_BASE_URL", "https://custom-api.example.com")
        settings = Settings()
        assert settings.pokeapi_base_url == "https://custom-api.example.com"
