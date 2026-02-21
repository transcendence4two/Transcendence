from fastapi import APIRouter, Depends, status

from src.di_config import get_tournament_service
from src.domain.schemas.tournament import (
    TournamentCreateRequest,
    TournamentResponse,
)
from src.domain.services.tournament import TournamentService

router = APIRouter()


@router.post(
    "",
    response_model=TournamentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tournament(
    request: TournamentCreateRequest,
    tournament_service: TournamentService = Depends(get_tournament_service),
):
    created_tournament = await tournament_service.create_tournament(request)
    return TournamentResponse.model_validate(created_tournament)


@router.get(
    "/{tournament_id}",
    response_model=TournamentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_tournament_by_id(
    tournament_id: str,
    tournament_service: TournamentService = Depends(get_tournament_service),
):
    tournament = await tournament_service.get_tournament_by_id(tournament_id)
    return TournamentResponse.model_validate(tournament)
