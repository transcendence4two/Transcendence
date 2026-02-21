import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTournamentEndpoints:
    async def test_health_check_returns_healthy(self, client: AsyncClient):
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    async def test_create_tournament_success(self, client: AsyncClient):
        payload = {
            "name": "Internal Championship",
            "created_by": "allandantas21",
        }

        response = await client.post("/tournaments", json=payload)

        assert response.status_code == 201
        response_body = response.json()
        assert response_body["name"] == payload["name"]
        assert response_body["created_by"] == payload["created_by"]
        assert response_body["status"] == "draft"
        assert "id" in response_body

    async def test_create_tournament_with_invalid_payload(self, client: AsyncClient):
        invalid_payload = {
            "name": "",
            "created_by": "allandantas21",
        }

        response = await client.post("/tournaments", json=invalid_payload)

        assert response.status_code == 422

    async def test_get_tournament_by_id_success(self, client: AsyncClient):
        payload = {
            "name": "42 Tournament",
            "created_by": "mvrga",
        }
        create_response = await client.post("/tournaments", json=payload)
        tournament_identifier = create_response.json()["id"]

        get_response = await client.get(f"/tournaments/{tournament_identifier}")

        assert get_response.status_code == 200
        response_body = get_response.json()
        assert response_body["id"] == tournament_identifier
        assert response_body["name"] == payload["name"]
        assert response_body["created_by"] == payload["created_by"]

    async def test_get_tournament_by_id_not_found(self, client: AsyncClient):
        response = await client.get(
            "/tournaments/00000000-0000-0000-0000-000000000000",
        )

        assert response.status_code == 404
        response_body = response.json()
        assert response_body["error_type"] == "TOURNAMENT_NOT_FOUND"
