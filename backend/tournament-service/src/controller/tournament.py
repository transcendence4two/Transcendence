from fastapi import APIRouter, Depends, status

from src.core.webhook_auth import require_valid_webhook_token
from src.di_config import get_tournament_service
from src.domain.contracts import TournamentManager
from src.domain.models.tournament import MatchPlayerSnapshot, MatchRecord
from src.domain.schemas.tournament import (
    MatchmakingQueueEntryResponse,
    MatchPlayerSnapshotResponse,
    MatchRecordResponse,
    MatchRecordSaveRequest,
    MatchRecordSaveResponse,
    PlayerStatsResponse,
    TournamentCreateRequest,
    TournamentJoinQueueRequest,
    TournamentMatchResponse,
    TournamentMatchResultRequest,
    TournamentParticipantRegisterRequest,
    TournamentParticipantResponse,
    TournamentResponse,
)

router = APIRouter()


def _build_match_record_save_response(
    match_record: MatchRecord,
    match_players: list[MatchPlayerSnapshot],
) -> MatchRecordSaveResponse:
    return MatchRecordSaveResponse(
        match_record=MatchRecordResponse.model_validate(match_record),
        players=[
            MatchPlayerSnapshotResponse.model_validate(match_player)
            for match_player in match_players
        ],
    )


@router.post(
    "",
    response_model=TournamentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tournament(
    request: TournamentCreateRequest,
    tournament_service: TournamentManager = Depends(get_tournament_service),
):
    created_tournament = await tournament_service.create_tournament(request)
    return TournamentResponse.model_validate(created_tournament)


@router.post(
    "/join",
    response_model=MatchmakingQueueEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def join_matchmaking_queue(
    request: TournamentJoinQueueRequest,
    tournament_service: TournamentManager = Depends(get_tournament_service),
):
    queue_entry = await tournament_service.join_matchmaking_queue(request)
    return MatchmakingQueueEntryResponse.model_validate(queue_entry)


@router.post(
    "/save",
    response_model=MatchRecordSaveResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_match_record(
    request: MatchRecordSaveRequest,
    tournament_service: TournamentManager = Depends(get_tournament_service),
):
    match_record, match_players = await tournament_service.save_match_record(request)
    return _build_match_record_save_response(
        match_record=match_record,
        match_players=match_players,
    )


@router.post(
    "/webhooks/game-match-finished",
    response_model=MatchRecordSaveResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_match_record_from_game_webhook(
    request: MatchRecordSaveRequest,
    _validated_webhook_token: None = Depends(require_valid_webhook_token),
    tournament_service: TournamentManager = Depends(get_tournament_service),
):
    match_record, match_players = await tournament_service.save_match_record(request)
    return _build_match_record_save_response(
        match_record=match_record,
        match_players=match_players,
    )


@router.get(
    "/{tournament_id}",
    response_model=TournamentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_tournament_by_id(
    tournament_id: str,
    tournament_service: TournamentManager = Depends(get_tournament_service),
):
    tournament = await tournament_service.get_tournament_by_id(tournament_id)
    return TournamentResponse.model_validate(tournament)


@router.post(
    "/{tournament_id}/participants/register",
    response_model=TournamentParticipantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_participant(
    tournament_id: str,
    request: TournamentParticipantRegisterRequest,
    tournament_service: TournamentManager = Depends(get_tournament_service),
):
    participant = await tournament_service.register_participant(
        tournament_id=tournament_id,
        payload=request,
    )
    return TournamentParticipantResponse.model_validate(participant)


@router.get(
    "/{tournament_id}/participants",
    response_model=list[TournamentParticipantResponse],
    status_code=status.HTTP_200_OK,
)
async def list_participants(
    tournament_id: str,
    tournament_service: TournamentManager = Depends(get_tournament_service),
):
    participants = await tournament_service.list_tournament_participants(tournament_id)
    return [
        TournamentParticipantResponse.model_validate(participant)
        for participant in participants
    ]


@router.post(
    "/{tournament_id}/start",
    response_model=list[TournamentMatchResponse],
    status_code=status.HTTP_201_CREATED,
)
async def start_tournament(
    tournament_id: str,
    tournament_service: TournamentManager = Depends(get_tournament_service),
):
    generated_matches = await tournament_service.start_tournament(tournament_id)
    return [TournamentMatchResponse.model_validate(match) for match in generated_matches]


@router.get(
    "/{tournament_id}/matches",
    response_model=list[TournamentMatchResponse],
    status_code=status.HTTP_200_OK,
)
async def list_matches(
    tournament_id: str,
    tournament_service: TournamentManager = Depends(get_tournament_service),
):
    matches = await tournament_service.list_tournament_matches(tournament_id)
    return [TournamentMatchResponse.model_validate(match) for match in matches]


@router.post(
    "/{tournament_id}/matches/{match_id}/result",
    response_model=TournamentMatchResponse,
    status_code=status.HTTP_200_OK,
)
async def register_match_result(
    tournament_id: str,
    match_id: str,
    request: TournamentMatchResultRequest,
    tournament_service: TournamentManager = Depends(get_tournament_service),
):
    updated_match = await tournament_service.register_match_result(
        tournament_id=tournament_id,
        match_id=match_id,
        payload=request,
    )
    return TournamentMatchResponse.model_validate(updated_match)


@router.get(
    "/stats/players/{user_id}",
    response_model=PlayerStatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_player_stats(
    user_id: str,
    tournament_service: TournamentManager = Depends(get_tournament_service),
):
    player_stats = await tournament_service.get_player_stats(user_id)
    if player_stats is None:
        return PlayerStatsResponse(
            user_id=user_id,
            display_name="unknown",
            tournaments_played=0,
            matches_played=0,
            wins=0,
            losses=0,
            total_points=0,
        )
    return PlayerStatsResponse.model_validate(player_stats)
