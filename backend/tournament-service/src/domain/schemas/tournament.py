from datetime import datetime

from pydantic import BaseModel, Field


class TournamentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    created_by: str = Field(..., min_length=1, max_length=255)


class TournamentResponse(BaseModel):
    id: str
    name: str
    status: str
    created_by: str

    model_config = {"from_attributes": True}


class TournamentParticipantRegisterRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)


class TournamentParticipantResponse(BaseModel):
    id: str
    tournament_id: str
    user_id: str
    display_name: str
    wins: int
    losses: int
    total_points: int

    model_config = {"from_attributes": True}


class TournamentMatchResponse(BaseModel):
    id: str
    tournament_id: str
    round_number: int
    match_order: int
    player_one_participant_id: str
    player_two_participant_id: str
    winner_participant_id: str | None
    status: str
    player_one_score: int | None
    player_two_score: int | None

    model_config = {"from_attributes": True}


class TournamentMatchResultRequest(BaseModel):
    winner_participant_id: str = Field(..., min_length=1, max_length=255)
    player_one_score: int = Field(..., ge=0)
    player_two_score: int = Field(..., ge=0)


class PlayerStatsResponse(BaseModel):
    user_id: str
    display_name: str
    tournaments_played: int
    matches_played: int
    wins: int
    losses: int
    total_points: int

    model_config = {"from_attributes": True}


class TournamentJoinQueueRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    skill_rating: int | None = Field(default=None, ge=0)
    preferred_game_mode: str = Field(default="pong_1v1", min_length=1, max_length=64)
    tournament_id: str | None = Field(default=None, min_length=1, max_length=255)


class MatchmakingQueueEntryResponse(BaseModel):
    id: str
    user_id: str
    display_name: str
    skill_rating: int | None
    preferred_game_mode: str
    tournament_id: str | None
    status: str
    game_session_id: str | None = None

    model_config = {"from_attributes": True}


class MatchmakingStatusResponse(BaseModel):
    user_id: str
    status: str
    game_session_id: str | None = None


class MatchPlayerSnapshotSaveRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    participant_id: str | None = Field(default=None, min_length=1, max_length=255)
    player_side: str | None = Field(default=None, min_length=1, max_length=32)
    score: int = Field(default=0, ge=0)
    is_winner: bool = False
    disconnect_count: int = Field(default=0, ge=0)
    latency_average_ms: int | None = Field(default=None, ge=0)
    latency_max_ms: int | None = Field(default=None, ge=0)


class MatchRecordSaveRequest(BaseModel):
    game_service_match_id: str | None = Field(default=None, min_length=1, max_length=255)
    tournament_id: str | None = Field(default=None, min_length=1, max_length=255)
    tournament_match_id: str | None = Field(default=None, min_length=1, max_length=255)
    game_room_id: str | None = Field(default=None, min_length=1, max_length=255)
    game_mode: str = Field(..., min_length=1, max_length=64)
    status: str = Field(default="finished", min_length=1, max_length=32)
    winner_user_id: str | None = Field(default=None, min_length=1, max_length=255)
    winning_reason: str | None = Field(default=None, min_length=1, max_length=64)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: int | None = Field(default=None, ge=0)
    players: list[MatchPlayerSnapshotSaveRequest] = Field(..., min_length=2)


class MatchPlayerSnapshotResponse(BaseModel):
    id: str
    match_record_id: str
    user_id: str
    display_name: str
    participant_id: str | None
    player_side: str | None
    score: int
    is_winner: bool
    disconnect_count: int
    latency_average_ms: int | None
    latency_max_ms: int | None

    model_config = {"from_attributes": True}


class MatchRecordResponse(BaseModel):
    id: str
    game_service_match_id: str | None
    tournament_id: str | None
    tournament_match_id: str | None
    game_room_id: str | None
    game_mode: str
    status: str
    winner_user_id: str | None
    winning_reason: str | None
    duration_seconds: int | None

    model_config = {"from_attributes": True}


class MatchRecordSaveResponse(BaseModel):
    match_record: MatchRecordResponse
    players: list[MatchPlayerSnapshotResponse]
