from typing import Any

from src.models import AllBerryStatsResponse, Berry, BerryListResponse


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
