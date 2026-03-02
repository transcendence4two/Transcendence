from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TournamentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    FINISHED = "finished"


class MatchStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default=TournamentStatus.DRAFT.value)
    created_by = Column(String, nullable=False)
    champion_user_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


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
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


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
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
