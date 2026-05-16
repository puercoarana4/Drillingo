import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RadarScores(BaseModel):
    """Per-module average scores for the radar chart (Req 9.2)."""
    reading: float = 0.0
    listening: float = 0.0
    writing: float = 0.0
    speaking: float = 0.0
    vocabulary: float = 0.0


class OralHistoryPoint(BaseModel):
    """Single data point for the oral history line chart (Req 9.4)."""
    submitted_at: datetime
    fluency_score: int
    pronunciation_score: int


class LevelHistoryPoint(BaseModel):
    """Single data point for the level progression bar chart (Req 9.1)."""
    date: datetime
    level_band: str


class DashboardResponse(BaseModel):
    """
    All dashboard metrics in a single response (Req 9.5).
    Must be returned in < 500ms.
    """
    # User identity & level
    user_id: uuid.UUID
    level_band: str
    xp_total: int

    # Streak (Req 9.6)
    current_streak: int
    longest_streak: int

    # Radar chart — per-module scores (Req 9.2)
    radar: RadarScores

    # Vocabulary mastery count (Req 9.3)
    vocabulary_mastered_count: int

    # Oral history — last 30 reports (Req 9.4)
    oral_history: list[OralHistoryPoint] = []

    # Level progression history (Req 9.1)
    level_history: list[LevelHistoryPoint] = []
