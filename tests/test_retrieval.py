from typing import Any

import pytest
from fastapi.testclient import TestClient


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
