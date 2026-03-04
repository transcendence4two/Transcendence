import logging
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import asc, desc, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.contracts import GameServiceClient, TournamentManager
from src.domain.exceptions import (

    DatabaseError,
    MatchmakingQueueError,
    MatchRecordValidationError,
    TournamentMatchNotFoundError,
    TournamentMatchResultError,
    TournamentNotFoundError,
    TournamentParticipantError,
    TournamentStateError,
)
from src.domain.models.tournament import (
    MatchPlayerSnapshot,
    MatchRecord,
    MatchRecordStatus,
    MatchmakingQueueEntry,
    MatchmakingQueueStatus,
    MatchmakingTransactionLock,
    MatchStatus,
    PlayerStats,
    Tournament,
    TournamentMatch,
    TournamentParticipant,
    TournamentStatus,
)
from src.domain.schemas.tournament import (
    MatchRecordSaveRequest,
    TournamentCreateRequest,
    TournamentJoinQueueRequest,
    TournamentMatchResultRequest,
    TournamentParticipantRegisterRequest,
)


logger = logging.getLogger(__name__)


class TournamentService(TournamentManager):
    """Service for tournament operations."""

    MATCHMAKING_LOCK_NAME = "global_matchmaking_join"

    def __init__(
        self,
        session: AsyncSession,
        game_client: GameServiceClient | None = None,
    ):
        self.session = session
        self._game_client = game_client

    @staticmethod
    def _to_utc_naive(timestamp_value: datetime | None) -> datetime | None:
        if timestamp_value is None:
            return None
        if timestamp_value.tzinfo is None:
            return timestamp_value
        return timestamp_value.astimezone(timezone.utc).replace(tzinfo=None)

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

    async def join_matchmaking_queue(
        self,
        payload: TournamentJoinQueueRequest,
    ) -> MatchmakingQueueEntry:
        normalized_user_id = payload.user_id.strip()
        normalized_display_name = payload.display_name.strip()
        normalized_game_mode = payload.preferred_game_mode.strip()
        normalized_tournament_id = (
            payload.tournament_id.strip() if payload.tournament_id else None
        )

        queue_entry: MatchmakingQueueEntry | None = None
        acquired_lock = False

        try:
            try:
                await self._acquire_matchmaking_transaction_lock()
            except DatabaseError:
                raise MatchmakingQueueError(
                    "Matchmaking is busy, please try again in a moment"
                )
            acquired_lock = True
            await self._ensure_user_not_already_in_matchmaking_queue(normalized_user_id)

            queue_entry = MatchmakingQueueEntry(
                id=str(uuid4()),
                user_id=normalized_user_id,
                display_name=normalized_display_name,
                skill_rating=payload.skill_rating,
                preferred_game_mode=normalized_game_mode,
                tournament_id=normalized_tournament_id,
                status=MatchmakingQueueStatus.QUEUED.value,
            )

            self.session.add(queue_entry)
            await self.session.flush()
            matched_opponent = await self._claim_matchmaking_opponent(
                preferred_game_mode=normalized_game_mode,
                tournament_id=normalized_tournament_id,
                excluded_user_id=normalized_user_id,
            )
            if matched_opponent is not None:
                match_timestamp = self._to_utc_naive(datetime.now(timezone.utc))
                queue_entry.status = MatchmakingQueueStatus.MATCHED.value
                queue_entry.matched_at = match_timestamp

                game_session_id = await self._create_game_session_for_match(
                    player1_user_id=matched_opponent.user_id,
                    player2_user_id=normalized_user_id,
                )
                if game_session_id:
                    queue_entry.game_session_id = game_session_id
                    matched_opponent.game_session_id = game_session_id

            await self._release_matchmaking_transaction_lock()
            acquired_lock = False
            await self.session.commit()
            await self.session.refresh(queue_entry)
            return queue_entry
        except MatchmakingQueueError:
            raise
        except IntegrityError as integrity_exception:
            await self.session.rollback()
            raise MatchmakingQueueError("Player is already queued for matchmaking") from (
                integrity_exception
            )
        except SQLAlchemyError as database_exception:
            await self.session.rollback()
            raise DatabaseError("Failed to enqueue player in matchmaking") from database_exception
        finally:
            if acquired_lock:
                await self.session.rollback()

    async def save_match_record(
        self,
        payload: MatchRecordSaveRequest,
    ) -> tuple[MatchRecord, list[MatchPlayerSnapshot]]:
        self._validate_match_record_payload(payload)

        normalized_status = payload.status.strip().lower()
        match_record = MatchRecord(
            id=str(uuid4()),
            game_service_match_id=payload.game_service_match_id,
            tournament_id=payload.tournament_id,
            tournament_match_id=payload.tournament_match_id,
            game_room_id=payload.game_room_id,
            game_mode=payload.game_mode.strip(),
            status=normalized_status,
            winner_user_id=payload.winner_user_id,
            winning_reason=payload.winning_reason,
            started_at=self._to_utc_naive(payload.started_at),
            ended_at=self._to_utc_naive(payload.ended_at),
            duration_seconds=payload.duration_seconds,
        )
        self.session.add(match_record)
        await self.session.flush()

        saved_snapshots: list[MatchPlayerSnapshot] = []
        for player_snapshot in payload.players:
            persisted_snapshot = MatchPlayerSnapshot(
                id=str(uuid4()),
                match_record_id=match_record.id,
                user_id=player_snapshot.user_id.strip(),
                display_name=player_snapshot.display_name.strip(),
                participant_id=player_snapshot.participant_id,
                player_side=player_snapshot.player_side,
                score=player_snapshot.score,
                is_winner=player_snapshot.is_winner,
                disconnect_count=player_snapshot.disconnect_count,
                latency_average_ms=player_snapshot.latency_average_ms,
                latency_max_ms=player_snapshot.latency_max_ms,
            )
            saved_snapshots.append(persisted_snapshot)
            self.session.add(persisted_snapshot)

        await self.session.flush()

        for persisted_snapshot in saved_snapshots:
            await self._upsert_player_stats_from_match_snapshot(persisted_snapshot)

        if payload.tournament_match_id is not None:
            await self._sync_tournament_match_from_match_record(
                match_record=match_record,
                saved_snapshots=saved_snapshots,
            )

        await self._deactivate_matchmaking_entries_for_users(
            user_identifiers=[
                persisted_snapshot.user_id for persisted_snapshot in saved_snapshots
            ]
        )

        try:
            await self.session.commit()
            await self.session.refresh(match_record)
            return match_record, saved_snapshots
        except SQLAlchemyError as database_exception:
            await self.session.rollback()
            raise DatabaseError("Failed to persist match record") from database_exception

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

    async def _ensure_user_not_already_in_matchmaking_queue(self, user_id: str) -> None:
        statement = select(MatchmakingQueueEntry).where(
            MatchmakingQueueEntry.user_id == user_id,
            MatchmakingQueueEntry.status.in_(
                [
                    MatchmakingQueueStatus.QUEUED.value,
                    MatchmakingQueueStatus.MATCHED.value,
                ]
            ),
        )
        try:
            query_result = await self.session.execute(statement)
            existing_queue_entry = query_result.scalar_one_or_none()
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to validate matchmaking queue entry") from database_exception

        if existing_queue_entry is not None:
            raise MatchmakingQueueError("Player is already queued for matchmaking")

    async def _deactivate_matchmaking_entries_for_users(
        self,
        user_identifiers: list[str],
    ) -> None:
        if not user_identifiers:
            return

        unique_user_identifiers = list(dict.fromkeys(user_identifiers))
        update_statement = (
            update(MatchmakingQueueEntry)
            .where(
                MatchmakingQueueEntry.user_id.in_(unique_user_identifiers),
                MatchmakingQueueEntry.status.in_(
                    [
                        MatchmakingQueueStatus.QUEUED.value,
                        MatchmakingQueueStatus.MATCHED.value,
                    ]
                ),
            )
            .values(status=MatchmakingQueueStatus.EXPIRED.value)
        )
        try:
            await self.session.execute(update_statement)
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to deactivate matchmaking entries") from (
                database_exception
            )

    async def _acquire_matchmaking_transaction_lock(self) -> None:
        matchmaking_lock = MatchmakingTransactionLock(
            lock_name=self.MATCHMAKING_LOCK_NAME
        )
        self.session.add(matchmaking_lock)
        try:
            await self.session.flush()
        except IntegrityError as integrity_exception:
            await self.session.rollback()
            raise DatabaseError("Failed to acquire matchmaking transaction lock") from (
                integrity_exception
            )

    async def _release_matchmaking_transaction_lock(self) -> None:
        matchmaking_lock = await self.session.get(
            MatchmakingTransactionLock,
            self.MATCHMAKING_LOCK_NAME,
        )
        if matchmaking_lock is None:
            return
        await self.session.delete(matchmaking_lock)
        await self.session.flush()

    async def _claim_matchmaking_opponent(
        self,
        preferred_game_mode: str,
        tournament_id: str | None,
        excluded_user_id: str,
    ) -> MatchmakingQueueEntry | None:
        statement = (
            select(MatchmakingQueueEntry)
            .where(
                MatchmakingQueueEntry.status == MatchmakingQueueStatus.QUEUED.value,
                MatchmakingQueueEntry.preferred_game_mode == preferred_game_mode,
                MatchmakingQueueEntry.user_id != excluded_user_id,
            )
            .order_by(asc(MatchmakingQueueEntry.joined_at))
            .limit(1)
        )
        if tournament_id is None:
            statement = statement.where(MatchmakingQueueEntry.tournament_id.is_(None))
        else:
            statement = statement.where(MatchmakingQueueEntry.tournament_id == tournament_id)
        if self.session.bind is not None and self.session.bind.dialect.name == "postgresql":
            statement = statement.with_for_update(skip_locked=True)

        try:
            query_result = await self.session.execute(statement)
            matched_opponent = query_result.scalars().first()
            if matched_opponent is None:
                return None

            match_timestamp = self._to_utc_naive(datetime.now(timezone.utc))
            update_statement = (
                update(MatchmakingQueueEntry)
                .where(
                    MatchmakingQueueEntry.id == matched_opponent.id,
                    MatchmakingQueueEntry.status == MatchmakingQueueStatus.QUEUED.value,
                )
                .values(
                    status=MatchmakingQueueStatus.MATCHED.value,
                    matched_at=match_timestamp,
                )
            )
            update_result = await self.session.execute(update_statement)
            if update_result.rowcount != 1:
                return None

            matched_opponent.status = MatchmakingQueueStatus.MATCHED.value
            matched_opponent.matched_at = match_timestamp
            return matched_opponent
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to find matchmaking opponent") from database_exception

    def _validate_match_record_payload(self, payload: MatchRecordSaveRequest) -> None:
        if payload.ended_at and payload.started_at and payload.ended_at < payload.started_at:
            raise MatchRecordValidationError("ended_at cannot be earlier than started_at")

        winner_identifiers_in_payload = {
            player_snapshot.user_id
            for player_snapshot in payload.players
            if player_snapshot.is_winner
        }
        if len(winner_identifiers_in_payload) > 1:
            raise MatchRecordValidationError("Only one winner is allowed per match")

        if payload.winner_user_id is not None:
            payload_winner_user_id = payload.winner_user_id.strip()
            valid_user_identifiers = {player.user_id for player in payload.players}
            if payload_winner_user_id not in valid_user_identifiers:
                raise MatchRecordValidationError("winner_user_id must belong to a match player")

            if winner_identifiers_in_payload and payload_winner_user_id not in winner_identifiers_in_payload:
                raise MatchRecordValidationError(
                    "winner_user_id must match the winner snapshot entry"
                )

    async def _upsert_player_stats_from_match_snapshot(
        self,
        persisted_snapshot: MatchPlayerSnapshot,
    ) -> None:
        statement = select(PlayerStats).where(
            PlayerStats.user_id == persisted_snapshot.user_id
        )
        try:
            with self.session.no_autoflush:
                query_result = await self.session.execute(statement)
            player_stats = query_result.scalar_one_or_none()
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to update player stats from match snapshot") from database_exception

        if player_stats is None:
            player_stats = PlayerStats(
                user_id=persisted_snapshot.user_id,
                display_name=persisted_snapshot.display_name,
                tournaments_played=0,
                matches_played=0,
                wins=0,
                losses=0,
                total_points=0,
            )
            self.session.add(player_stats)

        player_stats.matches_played += 1
        if persisted_snapshot.is_winner:
            player_stats.wins += 1
        else:
            player_stats.losses += 1
        player_stats.total_points += persisted_snapshot.score

    async def _sync_tournament_match_from_match_record(
        self,
        match_record: MatchRecord,
        saved_snapshots: list[MatchPlayerSnapshot],
    ) -> None:
        if match_record.tournament_match_id is None:
            return

        statement = select(TournamentMatch).where(
            TournamentMatch.id == match_record.tournament_match_id
        )
        try:
            query_result = await self.session.execute(statement)
            tournament_match = query_result.scalar_one_or_none()
        except SQLAlchemyError as database_exception:
            raise DatabaseError("Failed to sync tournament match") from database_exception

        if tournament_match is None:
            raise TournamentMatchNotFoundError(
                f"Match '{match_record.tournament_match_id}' was not found"
            )

        score_by_participant_id = {
            snapshot.participant_id: snapshot.score
            for snapshot in saved_snapshots
            if snapshot.participant_id is not None
        }

        if tournament_match.player_one_participant_id in score_by_participant_id:
            tournament_match.player_one_score = score_by_participant_id[
                tournament_match.player_one_participant_id
            ]
        if tournament_match.player_two_participant_id in score_by_participant_id:
            tournament_match.player_two_score = score_by_participant_id[
                tournament_match.player_two_participant_id
            ]

        winner_snapshot = next(
            (snapshot for snapshot in saved_snapshots if snapshot.is_winner),
            None,
        )
        if winner_snapshot is not None and winner_snapshot.participant_id is not None:
            tournament_match.winner_participant_id = winner_snapshot.participant_id

        if match_record.status == MatchRecordStatus.FINISHED.value:
            tournament_match.status = MatchStatus.FINISHED.value
            tournament_match.completed_at = match_record.ended_at

    async def _create_game_session_for_match(
        self,
        player1_user_id: str,
        player2_user_id: str,
    ) -> str | None:
        if self._game_client is None:
            logger.warning("No game client configured; skipping session creation")
            return None
        try:
            return await self._game_client.create_session(
                player1_user_id=player1_user_id,
                player2_user_id=player2_user_id,
            )
        except Exception as exc:
            logger.error(
                "Failed to create game session: %s",
                exc,
                exc_info=True,
            )
            return None

    async def get_matchmaking_status(
        self,
        user_id: str,
    ) -> MatchmakingQueueEntry | None:
        statement = (
            select(MatchmakingQueueEntry)
            .where(
                MatchmakingQueueEntry.user_id == user_id,
                MatchmakingQueueEntry.status.in_(
                    [
                        MatchmakingQueueStatus.QUEUED.value,
                        MatchmakingQueueStatus.MATCHED.value,
                    ]
                ),
            )
            .order_by(desc(MatchmakingQueueEntry.joined_at))
            .limit(1)
        )
        try:
            query_result = await self.session.execute(statement)
            return query_result.scalar_one_or_none()
        except SQLAlchemyError as database_exception:
            raise DatabaseError(
                "Failed to fetch matchmaking status"
            ) from database_exception
