from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TournamentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    FINISHED = "finished"


class MatchStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class MatchmakingQueueStatus(str, Enum):
    QUEUED = "queued"
    MATCHED = "matched"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class MatchRecordStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default=TournamentStatus.DRAFT.value)
    created_by = Column(String, nullable=False)
    champion_user_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=utc_now_naive, nullable=False)
    updated_at = Column(DateTime, default=utc_now_naive, onupdate=utc_now_naive)


class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"

    id = Column(String, primary_key=True, index=True)
    tournament_id = Column(
        String,
        ForeignKey("tournaments.id"),
        nullable=False,
        index=True,
    )
    user_id = Column(String, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    wins = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)
    total_points = Column(Integer, nullable=False, default=0)
    joined_at = Column(DateTime, default=utc_now_naive, nullable=False)


class TournamentMatch(Base):
    __tablename__ = "tournament_matches"

    id = Column(String, primary_key=True, index=True)
    tournament_id = Column(
        String,
        ForeignKey("tournaments.id"),
        nullable=False,
        index=True,
    )
    round_number = Column(Integer, nullable=False)
    match_order = Column(Integer, nullable=False)
    player_one_participant_id = Column(
        String,
        ForeignKey("tournament_participants.id"),
        nullable=False,
    )
    player_two_participant_id = Column(
        String,
        ForeignKey("tournament_participants.id"),
        nullable=False,
    )
    winner_participant_id = Column(
        String,
        ForeignKey("tournament_participants.id"),
        nullable=True,
    )
    status = Column(String, nullable=False, default=MatchStatus.PENDING.value)
    player_one_score = Column(Integer, nullable=True)
    player_two_score = Column(Integer, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class PlayerStats(Base):
    __tablename__ = "player_stats"

    user_id = Column(String, primary_key=True, index=True)
    display_name = Column(String, nullable=False)
    tournaments_played = Column(Integer, nullable=False, default=0)
    matches_played = Column(Integer, nullable=False, default=0)
    wins = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)
    total_points = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=utc_now_naive, onupdate=utc_now_naive)


class MatchmakingQueueEntry(Base):
    __tablename__ = "matchmaking_queue_entries"
    __table_args__ = (
        Index(
            "uq_matchmaking_queue_entries_queued_user_id",
            "user_id",
            unique=True,
            sqlite_where=text("status = 'queued'"),
            postgresql_where=text("status = 'queued'"),
        ),
    )

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    skill_rating = Column(Integer, nullable=True)
    preferred_game_mode = Column(String, nullable=False, default="pong_1v1")
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=True, index=True)
    status = Column(String, nullable=False, default=MatchmakingQueueStatus.QUEUED.value)
    game_session_id = Column(String, nullable=True, index=True)
    joined_at = Column(DateTime, default=utc_now_naive, nullable=False)
    matched_at = Column(DateTime, nullable=True)


class MatchRecord(Base):
    __tablename__ = "match_records"

    id = Column(String, primary_key=True, index=True)
    game_service_match_id = Column(String, nullable=True, index=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=True, index=True)
    tournament_match_id = Column(
        String,
        ForeignKey("tournament_matches.id"),
        nullable=True,
        index=True,
    )
    game_room_id = Column(String, nullable=True, index=True)
    game_mode = Column(String, nullable=False)
    status = Column(String, nullable=False, default=MatchRecordStatus.FINISHED.value)
    winner_user_id = Column(String, nullable=True, index=True)
    winning_reason = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utc_now_naive, nullable=False)


class MatchPlayerSnapshot(Base):
    __tablename__ = "match_player_snapshots"

    id = Column(String, primary_key=True, index=True)
    match_record_id = Column(
        String,
        ForeignKey("match_records.id"),
        nullable=False,
        index=True,
    )
    user_id = Column(String, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    participant_id = Column(
        String,
        ForeignKey("tournament_participants.id"),
        nullable=True,
        index=True,
    )
    player_side = Column(String, nullable=True)
    score = Column(Integer, nullable=False, default=0)
    is_winner = Column(Boolean, nullable=False, default=False)
    disconnect_count = Column(Integer, nullable=False, default=0)
    latency_average_ms = Column(Integer, nullable=True)
    latency_max_ms = Column(Integer, nullable=True)


class MatchmakingTransactionLock(Base):
    __tablename__ = "matchmaking_transaction_locks"

    lock_name = Column(String, primary_key=True)
    locked_at = Column(DateTime, default=utc_now_naive, nullable=False)
