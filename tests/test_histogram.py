from typing import Any

from fastapi.testclient import TestClient


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
