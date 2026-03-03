import asyncio
import os
import tempfile
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.domain.models.tournament import (
    Base,
    MatchmakingQueueEntry,
    MatchmakingQueueStatus,
)
from src.domain.schemas.tournament import TournamentJoinQueueRequest
from src.domain.services.tournament import TournamentService

WEBHOOK_HEADER_NAME = "X-Webhook-Token"
WEBHOOK_SHARED_SECRET = "local-webhook-token"


def build_match_record_payload() -> dict:
    return {
        "game_service_match_id": "game-service-match-001",
        "game_room_id": "room-001",
        "game_mode": "pong_1v1",
        "status": "finished",
        "winner_user_id": "player_alpha",
        "winning_reason": "score",
        "started_at": "2026-02-27T10:00:00+00:00",
        "ended_at": "2026-02-27T10:03:30+00:00",
        "duration_seconds": 210,
        "players": [
            {
                "user_id": "player_alpha",
                "display_name": "Player Alpha",
                "player_side": "left",
                "score": 7,
                "is_winner": True,
            },
            {
                "user_id": "player_beta",
                "display_name": "Player Beta",
                "player_side": "right",
                "score": 4,
                "is_winner": False,
            },
        ],
    }


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

    async def test_join_matchmaking_queue_success_and_duplicate(self, client: AsyncClient):
        queue_payload = {
            "user_id": "queued_player",
            "display_name": "Queued Player",
            "preferred_game_mode": "pong_1v1",
        }
        first_join_response = await client.post("/tournaments/join", json=queue_payload)
        assert first_join_response.status_code == 201
        first_join_body = first_join_response.json()
        assert first_join_body["user_id"] == queue_payload["user_id"]
        assert first_join_body["status"] in {"queued", "matched"}

        duplicate_join_response = await client.post(
            "/tournaments/join",
            json=queue_payload,
        )
        assert duplicate_join_response.status_code == 409
        duplicate_join_body = duplicate_join_response.json()
        assert duplicate_join_body["error_type"] == "MATCHMAKING_QUEUE_ERROR"

    async def test_join_matchmaking_queue_handles_multiple_available_opponents(
        self,
        client: AsyncClient,
        db_session,
    ):
        db_session.add(
            MatchmakingQueueEntry(
                id=str(uuid4()),
                user_id="existing_player_one",
                display_name="Existing Player One",
                preferred_game_mode="pong_1v1",
                status=MatchmakingQueueStatus.QUEUED.value,
            )
        )
        db_session.add(
            MatchmakingQueueEntry(
                id=str(uuid4()),
                user_id="existing_player_two",
                display_name="Existing Player Two",
                preferred_game_mode="pong_1v1",
                status=MatchmakingQueueStatus.QUEUED.value,
            )
        )
        await db_session.commit()

        join_response = await client.post(
            "/tournaments/join",
            json={
                "user_id": "new_player",
                "display_name": "New Player",
                "preferred_game_mode": "pong_1v1",
            },
        )

        assert join_response.status_code == 201
        assert join_response.json()["status"] == "matched"

        duplicate_response = await client.post(
            "/tournaments/join",
            json={
                "user_id": "new_player",
                "display_name": "New Player",
                "preferred_game_mode": "pong_1v1",
            },
        )

        assert duplicate_response.status_code == 409
        assert duplicate_response.json()["error_type"] == "MATCHMAKING_QUEUE_ERROR"

    async def test_join_matchmaking_queue_serializes_concurrent_requests(self):
        database_file_descriptor, database_path = tempfile.mkstemp(suffix=".db")
        os.close(database_file_descriptor)
        database_url = f"sqlite+aiosqlite:///{database_path}"
        engine = create_async_engine(database_url, connect_args={"timeout": 30})

        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            async_session_factory = sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            async def join_queue(request_index: int) -> str:
                async with async_session_factory() as session:
                    tournament_service = TournamentService(session=session)
                    queue_payload = TournamentJoinQueueRequest(
                        user_id=f"concurrent_player_{request_index}",
                        display_name=f"Concurrent Player {request_index}",
                        preferred_game_mode="pong_1v1",
                    )
                    queue_entry = await tournament_service.join_matchmaking_queue(
                        queue_payload
                    )
                    return queue_entry.status

            join_results = await asyncio.gather(
                *(join_queue(request_index) for request_index in range(20))
            )

            assert len(join_results) == 20
            assert all(queue_status in {"queued", "matched"} for queue_status in join_results)

            async with async_session_factory() as verification_session:
                queued_query_result = await verification_session.execute(
                    select(MatchmakingQueueEntry).where(
                        MatchmakingQueueEntry.status
                        == MatchmakingQueueStatus.QUEUED.value
                    )
                )
                matched_query_result = await verification_session.execute(
                    select(MatchmakingQueueEntry).where(
                        MatchmakingQueueEntry.status
                        == MatchmakingQueueStatus.MATCHED.value
                    )
                )
                queued_entries = list(queued_query_result.scalars().all())
                matched_entries = list(matched_query_result.scalars().all())

            assert len(queued_entries) == 0
            assert len(matched_entries) == 20
        finally:
            await engine.dispose()
            os.remove(database_path)

    async def test_save_match_record_persists_match_and_players(self, client: AsyncClient):
        first_join_response = await client.post(
            "/tournaments/join",
            json={
                "user_id": "player_alpha",
                "display_name": "Player Alpha",
                "preferred_game_mode": "pong_1v1",
            },
        )
        second_join_response = await client.post(
            "/tournaments/join",
            json={
                "user_id": "player_beta",
                "display_name": "Player Beta",
                "preferred_game_mode": "pong_1v1",
            },
        )
        assert first_join_response.status_code == 201
        assert second_join_response.status_code == 201

        save_payload = build_match_record_payload()
        save_response = await client.post("/tournaments/save", json=save_payload)

        assert save_response.status_code == 201
        save_body = save_response.json()
        assert save_body["match_record"]["game_service_match_id"] == "game-service-match-001"
        assert save_body["match_record"]["winner_user_id"] == "player_alpha"
        assert len(save_body["players"]) == 2

        alpha_stats_response = await client.get("/tournaments/stats/players/player_alpha")
        alpha_stats_body = alpha_stats_response.json()
        assert alpha_stats_response.status_code == 200
        assert alpha_stats_body["wins"] >= 1
        assert alpha_stats_body["matches_played"] >= 1

        rejoin_response = await client.post(
            "/tournaments/join",
            json={
                "user_id": "player_alpha",
                "display_name": "Player Alpha",
                "preferred_game_mode": "pong_1v1",
            },
        )
        assert rejoin_response.status_code == 201

    async def test_webhook_save_requires_valid_token(self, client: AsyncClient):
        save_payload = build_match_record_payload()

        unauthorized_response = await client.post(
            "/tournaments/webhooks/game-match-finished",
            json=save_payload,
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.post(
            "/tournaments/webhooks/game-match-finished",
            json=save_payload,
            headers={WEBHOOK_HEADER_NAME: WEBHOOK_SHARED_SECRET},
        )
        assert authorized_response.status_code == 201
        authorized_response_body = authorized_response.json()
        assert authorized_response_body["match_record"]["winner_user_id"] == "player_alpha"
