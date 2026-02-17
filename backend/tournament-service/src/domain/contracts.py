from abc import ABC, abstractmethod

from src.domain.models.tournament import Tournament
from src.domain.schemas.tournament import TournamentCreateRequest


class TournamentManager(ABC):
    """Port for tournament operations."""

    @abstractmethod
    async def create_tournament(
        self,
        payload: TournamentCreateRequest,
    ) -> Tournament: ...

    @abstractmethod
    async def get_tournament_by_id(self, tournament_id: str) -> Tournament: ...
