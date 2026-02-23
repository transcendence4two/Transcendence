from pydantic import BaseModel, Field


class TournamentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    created_by: str = Field(..., min_length=1, max_length=255)


class TournamentResponse(BaseModel):
    id: str
    name: str
    status: str
    created_by: str

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True
