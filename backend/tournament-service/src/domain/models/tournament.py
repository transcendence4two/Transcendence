from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)


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
    scheduled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
