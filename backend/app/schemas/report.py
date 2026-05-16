import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class OralReportRequest(BaseModel):
    """
    Payload the user pastes from their external oral practice session.
    fluency_score and pronunciation_score are required (Req 7.1).
    raw_json is stored as JSONB without modification (Req 7.6).
    """

    session_duration_seconds: int
    fluency_score: int
    pronunciation_score: int
    notes: Optional[str] = None

    @field_validator("fluency_score", "pronunciation_score")
    @classmethod
    def score_in_range(cls, v: int) -> int:
        if not (0 <= v <= 100):
            raise ValueError("Score must be between 0 and 100")
        return v

    @field_validator("session_duration_seconds")
    @classmethod
    def duration_positive(cls, v: int) -> int:
        if v < 0:
            raise ValueError("session_duration_seconds must be non-negative")
        return v


class OralReportResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    fluency_score: int
    pronunciation_score: int
    session_duration_seconds: Optional[int] = None
    notes: Optional[str] = None
    submitted_at: datetime

    model_config = {"from_attributes": True}
