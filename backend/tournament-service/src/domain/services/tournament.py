from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import asc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.contracts import TournamentManager
from src.domain.exceptions import (
    DatabaseError,
    TournamentMatchNotFoundError,
    TournamentMatchResultError,
    TournamentNotFoundError,
    TournamentParticipantError,
    TournamentStateError,
)
from src.domain.models.tournament import (
    MatchStatus,
    PlayerStats,
    Tournament,
    TournamentMatch,
    TournamentParticipant,
    TournamentStatus,
)
from src.domain.schemas.tournament import (
    TournamentCreateRequest,
    TournamentMatchResultRequest,
    TournamentParticipantRegisterRequest,
)


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
            raise TournamentNotFoundError(f"Tournament '{tournament_id}' was not found")
        return tournament

    async def register_participant(
        self,
        tournament_id: str,
        payload: TournamentParticipantRegisterRequest,
    ) -> TournamentParticipant:
        tournament = await self.get_tournament_by_id(tournament_id)
        self._ensure_tournament_is_draft(tournament)

        await self._ensure_user_not_registered(
            tournament_id=tournament_id,
            user_id=payload.user_id.strip(),
        )

        participant = TournamentParticipant(
            id=str(uuid4()),
            tournament_id=tournament_id,
            user_id=payload.user_id.strip(),
            display_name=payload.display_name.strip(),
        )

        self.session.add(participant)
        try:
            await self.session.commit()
            await self.session.refresh(participant)
            return participant
        except SQLAlchemyError as database_exception:
            await self.session.rollback()
            raise DatabaseError("Failed to register participant") from database_exception

    async def list_tournament_participants(
        self,
        tournament_id: str,
    ) -> list[TournamentParticipant]:
        await self.get_tournament_by_id(tournament_id)

        statement = (
            select(TournamentParticipant)
            .where(TournamentParticipant.tournament_id == tournament_id)
            .order_by(asc(TournamentParticipant.joined_at))
        )
        try:
            query_result = await self.session.execute(statement)
            return list(query_result.scalars().all())
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to list tournament participants") from database_exception

    async def start_tournament(self, tournament_id: str) -> list[TournamentMatch]:
        tournament = await self.get_tournament_by_id(tournament_id)
        self._ensure_tournament_is_draft(tournament)

        participants = await self.list_tournament_participants(tournament_id)
        self._ensure_valid_participant_count(participants)

        first_round_matches = self._create_round_matches(
            tournament_id=tournament_id,
            participants=participants,
            round_number=1,
        )

        tournament.status = TournamentStatus.ACTIVE.value
        for tournament_match in first_round_matches:
            self.session.add(tournament_match)

        try:
            await self.session.commit()
            return first_round_matches
        except SQLAlchemyError as database_exception:
            await self.session.rollback()
            raise DatabaseError("Failed to start tournament") from database_exception

    async def list_tournament_matches(self, tournament_id: str) -> list[TournamentMatch]:
        await self.get_tournament_by_id(tournament_id)
        statement = (
            select(TournamentMatch)
            .where(TournamentMatch.tournament_id == tournament_id)
            .order_by(
                asc(TournamentMatch.round_number),
                asc(TournamentMatch.match_order),
            )
        )
        try:
            query_result = await self.session.execute(statement)
            return list(query_result.scalars().all())
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to list tournament matches") from database_exception

    async def register_match_result(
        self,
        tournament_id: str,
        match_id: str,
        payload: TournamentMatchResultRequest,
    ) -> TournamentMatch:
        tournament = await self.get_tournament_by_id(tournament_id)
        self._ensure_tournament_is_active(tournament)

        tournament_match = await self._get_match_or_raise(
            tournament_id=tournament_id,
            match_id=match_id,
        )
        self._ensure_match_is_result_ready(tournament_match, payload.winner_participant_id)

        player_one = await self._get_participant_or_raise(
            tournament_match.player_one_participant_id
        )
        player_two = await self._get_participant_or_raise(
            tournament_match.player_two_participant_id
        )
        winner_participant = player_one
        loser_participant = player_two
        winner_score = payload.player_one_score
        loser_score = payload.player_two_score

        if payload.winner_participant_id == player_two.id:
            winner_participant = player_two
            loser_participant = player_one
            winner_score = payload.player_two_score
            loser_score = payload.player_one_score

        tournament_match.winner_participant_id = winner_participant.id
        tournament_match.player_one_score = payload.player_one_score
        tournament_match.player_two_score = payload.player_two_score
        tournament_match.status = MatchStatus.FINISHED.value
        tournament_match.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)

        winner_participant.wins += 1
        winner_participant.total_points += winner_score
        loser_participant.losses += 1
        loser_participant.total_points += loser_score

        await self._upsert_player_stats(
            participant=winner_participant,
            did_win=True,
            scored_points=winner_score,
        )
        await self._upsert_player_stats(
            participant=loser_participant,
            did_win=False,
            scored_points=loser_score,
        )

        await self._advance_bracket_if_round_finished(
            tournament=tournament,
            current_round_number=tournament_match.round_number,
        )

        try:
            await self.session.commit()
            await self.session.refresh(tournament_match)
            return tournament_match
        except SQLAlchemyError as database_exception:
            await self.session.rollback()
            raise DatabaseError("Failed to register match result") from database_exception

    async def get_player_stats(self, user_id: str) -> PlayerStats | None:
        statement = select(PlayerStats).where(PlayerStats.user_id == user_id)
        try:
            query_result = await self.session.execute(statement)
            return query_result.scalar_one_or_none()
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to fetch player stats") from database_exception

    async def _persist_tournament(self, tournament: Tournament) -> Tournament:
        self.session.add(tournament)
        try:
            await self.session.commit()
            await self.session.refresh(tournament)
            return tournament
        except SQLAlchemyError as database_exception:
            await self.session.rollback()
            raise DatabaseError("Failed to create tournament") from database_exception

    def _ensure_tournament_is_draft(self, tournament: Tournament) -> None:
        if tournament.status != TournamentStatus.DRAFT.value:
            raise TournamentStateError("Tournament must be in draft state")

    def _ensure_tournament_is_active(self, tournament: Tournament) -> None:
        if tournament.status != TournamentStatus.ACTIVE.value:
            raise TournamentStateError("Tournament must be active")

    async def _ensure_user_not_registered(
        self,
        tournament_id: str,
        user_id: str,
    ) -> None:
        statement = select(TournamentParticipant).where(
            TournamentParticipant.tournament_id == tournament_id,
            TournamentParticipant.user_id == user_id,
        )
        try:
            query_result = await self.session.execute(statement)
            existing_participant = query_result.scalar_one_or_none()
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to validate participant uniqueness") from database_exception

        if existing_participant is not None:
            raise TournamentParticipantError("User is already registered in tournament")

    def _ensure_valid_participant_count(
        self,
        participants: list[TournamentParticipant],
    ) -> None:
        participant_count = len(participants)
        if participant_count < 2:
            raise TournamentParticipantError("Tournament requires at least 2 participants")

        if participant_count % 2 != 0:
            raise TournamentParticipantError("Tournament requires an even number of participants")

    def _create_round_matches(
        self,
        tournament_id: str,
        participants: list[TournamentParticipant],
        round_number: int,
    ) -> list[TournamentMatch]:
        created_matches: list[TournamentMatch] = []
        current_match_order = 1
        participant_index = 0

        while participant_index < len(participants):
            player_one = participants[participant_index]
            player_two = participants[participant_index + 1]
            created_matches.append(
                TournamentMatch(
                    id=str(uuid4()),
                    tournament_id=tournament_id,
                    round_number=round_number,
                    match_order=current_match_order,
                    player_one_participant_id=player_one.id,
                    player_two_participant_id=player_two.id,
                    status=MatchStatus.PENDING.value,
                )
            )
            participant_index += 2
            current_match_order += 1

        return created_matches

    async def _get_match_or_raise(
        self,
        tournament_id: str,
        match_id: str,
    ) -> TournamentMatch:
        statement = select(TournamentMatch).where(
            TournamentMatch.id == match_id,
            TournamentMatch.tournament_id == tournament_id,
        )
        try:
            query_result = await self.session.execute(statement)
            tournament_match = query_result.scalar_one_or_none()
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to fetch match") from database_exception

        if tournament_match is None:
            raise TournamentMatchNotFoundError(f"Match '{match_id}' was not found")
        return tournament_match

    async def _get_participant_or_raise(
        self,
        participant_id: str,
    ) -> TournamentParticipant:
        statement = select(TournamentParticipant).where(
            TournamentParticipant.id == participant_id
        )
        try:
            query_result = await self.session.execute(statement)
            participant = query_result.scalar_one_or_none()
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to fetch participant") from database_exception

        if participant is None:
            raise TournamentParticipantError("Participant does not exist")
        return participant

    def _ensure_match_is_result_ready(
        self,
        tournament_match: TournamentMatch,
        winner_participant_id: str,
    ) -> None:
        if tournament_match.status == MatchStatus.FINISHED.value:
            raise TournamentMatchResultError("Match result has already been registered")

        allowed_winner_identifiers = {
            tournament_match.player_one_participant_id,
            tournament_match.player_two_participant_id,
        }
        if winner_participant_id not in allowed_winner_identifiers:
            raise TournamentMatchResultError("Winner must be one of the match participants")

    async def _upsert_player_stats(
        self,
        participant: TournamentParticipant,
        did_win: bool,
        scored_points: int,
    ) -> None:
        statement = select(PlayerStats).where(PlayerStats.user_id == participant.user_id)
        try:
            query_result = await self.session.execute(statement)
            player_stats = query_result.scalar_one_or_none()
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to fetch player stats") from database_exception

        if player_stats is None:
            player_stats = PlayerStats(
                user_id=participant.user_id,
                display_name=participant.display_name,
                tournaments_played=1,
                matches_played=0,
                wins=0,
                losses=0,
                total_points=0,
            )
            self.session.add(player_stats)

        player_stats.matches_played += 1
        if did_win:
            player_stats.wins += 1
        else:
            player_stats.losses += 1
        player_stats.total_points += scored_points

    async def _advance_bracket_if_round_finished(
        self,
        tournament: Tournament,
        current_round_number: int,
    ) -> None:
        current_round_matches = await self._fetch_round_matches(
            tournament_id=tournament.id,
            round_number=current_round_number,
        )
        if any(match.status != MatchStatus.FINISHED.value for match in current_round_matches):
            return

        winner_identifiers = [
            match.winner_participant_id
            for match in current_round_matches
            if match.winner_participant_id is not None
        ]
        if len(winner_identifiers) == 1:
            champion_participant = await self._get_participant_or_raise(
                winner_identifiers[0]
            )
            tournament.status = TournamentStatus.FINISHED.value
            tournament.champion_user_id = champion_participant.user_id
            return

        winners = [
            await self._get_participant_or_raise(participant_id)
            for participant_id in winner_identifiers
        ]
        next_round_number = current_round_number + 1
        next_round_matches = self._create_round_matches(
            tournament_id=tournament.id,
            participants=winners,
            round_number=next_round_number,
        )
        for tournament_match in next_round_matches:
            self.session.add(tournament_match)

    async def _fetch_round_matches(
        self,
        tournament_id: str,
        round_number: int,
    ) -> list[TournamentMatch]:
        statement = (
            select(TournamentMatch)
            .where(
                TournamentMatch.tournament_id == tournament_id,
                TournamentMatch.round_number == round_number,
            )
            .order_by(asc(TournamentMatch.match_order))
        )
        try:
            query_result = await self.session.execute(statement)
            return list(query_result.scalars().all())
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to fetch round matches") from database_exception
