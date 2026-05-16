import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class LessonProgressRequest(BaseModel):
    lesson_id: uuid.UUID
    module_type: str  # reading | listening | writing | speaking
    score: int

    @field_validator("module_type")
    @classmethod
    def validate_module_type(cls, v: str) -> str:
        valid = {"reading", "listening", "writing", "speaking"}
        if v not in valid:
            raise ValueError(f"module_type must be one of {valid}")
        return v

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        if not (0 <= v <= 100):
            raise ValueError("score must be between 0 and 100")
        return v


class LessonProgressResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    lesson_id: uuid.UUID
    module_type: str
    score: int
    completed_at: datetime
    xp_awarded: int  # XP granted for this module completion

    model_config = {"from_attributes": True}


class ProgressSummaryResponse(BaseModel):
    """Aggregated progress summary for the authenticated user."""

    user_id: uuid.UUID
    level_band: str
    xp_total: int
    # Average score per module type (0–100), None if no data yet
    reading_avg: Optional[float] = None
    listening_avg: Optional[float] = None
    writing_avg: Optional[float] = None
    speaking_avg: Optional[float] = None
    total_lessons_completed: int = 0


class VocabularyProgressResponse(BaseModel):
    """Per-item vocabulary progress for the authenticated user."""

    vocabulary_item_id: uuid.UUID
    term: str
    definition: str
    example_sentence: Optional[str] = None
    dialect_segment: Optional[str] = None
    level_band: Optional[str] = None
    mastered: bool
    correct_count: int
    last_reviewed_at: Optional[datetime] = None
