from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.contracts import TournamentManager
from src.domain.exceptions import DatabaseError, TournamentNotFoundError
from src.domain.models.tournament import Tournament, TournamentStatus
from src.domain.schemas.tournament import TournamentCreateRequest


class TournamentService(TournamentManager):
    """Service for tournament operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_tournament(self, payload: TournamentCreateRequest) -> Tournament:
        tournament = Tournament(
            id=str(uuid4()),
            name=payload.name.strip(),
            status=TournamentStatus.DRAFT.value,
            created_by=payload.created_by.strip(),
        )
        return await self._persist_tournament(tournament)

    async def get_tournament_by_id(self, tournament_id: str) -> Tournament:
        statement = select(Tournament).where(Tournament.id == tournament_id)

        try:
            query_result = await self.session.execute(statement)
            tournament = query_result.scalar_one_or_none()
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to fetch tournament") from database_exception

        if tournament is None:
            raise TournamentNotFoundError(
                f"Tournament '{tournament_id}' was not found",
            )
        return tournament

    async def _persist_tournament(self, tournament: Tournament) -> Tournament:
        self.session.add(tournament)
        try:
            await self.session.commit()
            await self.session.refresh(tournament)
            return tournament
        except SQLAlchemyError as database_exception:
            await self.session.rollback()
            raise DatabaseError("Failed to create tournament") from database_exception
