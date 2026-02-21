from abc import ABC, abstractmethod

from src.domain.models.tournament import (
    PlayerStats,
    Tournament,
    TournamentMatch,
    TournamentParticipant,
)
from src.domain.schemas.tournament import (
    TournamentCreateRequest,
    TournamentMatchResultRequest,
    TournamentParticipantRegisterRequest,
)


class TournamentManager(ABC):
    """Port for tournament operations."""

    @abstractmethod
    async def create_tournament(
        self,
        payload: TournamentCreateRequest,
    ) -> Tournament: ...

    @abstractmethod
    async def get_tournament_by_id(self, tournament_id: str) -> Tournament: ...

    @abstractmethod
    async def register_participant(
        self,
        tournament_id: str,
        payload: TournamentParticipantRegisterRequest,
    ) -> TournamentParticipant: ...

    @abstractmethod
    async def list_tournament_participants(
        self,
        tournament_id: str,
    ) -> list[TournamentParticipant]: ...

    @abstractmethod
    async def start_tournament(self, tournament_id: str) -> list[TournamentMatch]: ...

    @abstractmethod
    async def list_tournament_matches(self, tournament_id: str) -> list[TournamentMatch]: ...

    @abstractmethod
    async def register_match_result(
        self,
        tournament_id: str,
        match_id: str,
        payload: TournamentMatchResultRequest,
    ) -> TournamentMatch: ...

    @abstractmethod
    async def get_player_stats(self, user_id: str) -> PlayerStats | None: ...
