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

    async def test_register_participants_and_start_tournament(self, client: AsyncClient):
        create_response = await client.post(
            "/tournaments",
            json={"name": "Spring Cup", "created_by": "admin"},
        )
        tournament_id = create_response.json()["id"]

        participants_payload = [
            {"user_id": "user_1", "display_name": "Player One"},
            {"user_id": "user_2", "display_name": "Player Two"},
            {"user_id": "user_3", "display_name": "Player Three"},
            {"user_id": "user_4", "display_name": "Player Four"},
        ]
        for participant_payload in participants_payload:
            participant_response = await client.post(
                f"/tournaments/{tournament_id}/participants/register",
                json=participant_payload,
            )
            assert participant_response.status_code == 201

        start_response = await client.post(f"/tournaments/{tournament_id}/start")
        assert start_response.status_code == 201
        round_one_matches = start_response.json()
        assert len(round_one_matches) == 2

        matches_response = await client.get(f"/tournaments/{tournament_id}/matches")
        assert matches_response.status_code == 200
        assert len(matches_response.json()) == 2

    async def test_register_result_generates_next_round(self, client: AsyncClient):
        create_response = await client.post(
            "/tournaments",
            json={"name": "Final Bracket", "created_by": "admin"},
        )
        tournament_id = create_response.json()["id"]

        participants_payload = [
            {"user_id": "user_a", "display_name": "Player A"},
            {"user_id": "user_b", "display_name": "Player B"},
            {"user_id": "user_c", "display_name": "Player C"},
            {"user_id": "user_d", "display_name": "Player D"},
        ]
        for participant_payload in participants_payload:
            participant_response = await client.post(
                f"/tournaments/{tournament_id}/participants/register",
                json=participant_payload,
            )
            assert participant_response.status_code == 201

        start_response = await client.post(f"/tournaments/{tournament_id}/start")
        round_one_matches = start_response.json()

        first_match = round_one_matches[0]
        second_match = round_one_matches[1]
        first_result_response = await client.post(
            f"/tournaments/{tournament_id}/matches/{first_match['id']}/result",
            json={
                "winner_participant_id": first_match["player_one_participant_id"],
                "player_one_score": 7,
                "player_two_score": 3,
            },
        )
        assert first_result_response.status_code == 200

        second_result_response = await client.post(
            f"/tournaments/{tournament_id}/matches/{second_match['id']}/result",
            json={
                "winner_participant_id": second_match["player_two_participant_id"],
                "player_one_score": 2,
                "player_two_score": 8,
            },
        )
        assert second_result_response.status_code == 200

        matches_response = await client.get(f"/tournaments/{tournament_id}/matches")
        all_matches = matches_response.json()
        assert len(all_matches) == 3
        final_match = all_matches[2]
        assert final_match["round_number"] == 2

        stats_response = await client.get("/tournaments/stats/players/user_a")
        stats_payload = stats_response.json()
        assert stats_response.status_code == 200
        assert stats_payload["wins"] == 1
        assert stats_payload["matches_played"] == 1
