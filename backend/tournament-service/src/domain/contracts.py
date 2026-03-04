from abc import ABC, abstractmethod

from src.domain.models.tournament import (
    MatchRecord,
    MatchmakingQueueEntry,
    MatchPlayerSnapshot,
    PlayerStats,
    Tournament,
    TournamentMatch,
    TournamentParticipant,
)
from src.domain.schemas.tournament import (
    MatchRecordSaveRequest,
    TournamentCreateRequest,
    TournamentJoinQueueRequest,
    TournamentMatchResultRequest,
    TournamentParticipantRegisterRequest,
)


class GameServiceClient(ABC):
    """Port for communication with the game-service."""

    @abstractmethod
    async def create_session(
        self,
        player1_user_id: str,
        player2_user_id: str,
    ) -> str:
        """Create a game session and return the session_id."""
        ...


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

    @abstractmethod
    async def join_matchmaking_queue(
        self,
        payload: TournamentJoinQueueRequest,
    ) -> MatchmakingQueueEntry: ...

    @abstractmethod
    async def save_match_record(
        self,
        payload: MatchRecordSaveRequest,
    ) -> tuple[MatchRecord, list[MatchPlayerSnapshot]]: ...

    @abstractmethod
    async def get_matchmaking_status(
        self,
        user_id: str,
    ) -> MatchmakingQueueEntry | None: ...
