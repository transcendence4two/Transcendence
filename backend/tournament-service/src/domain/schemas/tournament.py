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
