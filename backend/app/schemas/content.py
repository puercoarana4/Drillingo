import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VocabularyItemResponse(BaseModel):
    """
    Response schema for a vocabulary item.
    dialect_segment is always included so the client can identify the region (Req 3.4).
    """

    id: uuid.UUID
    term: str
    definition: str
    example_sentence: Optional[str] = None
    # Always present in responses so the client can identify East Coast vs Midwest (Req 3.4)
    dialect_segment: Optional[str] = None
    level_band: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LessonResponse(BaseModel):
    """Lightweight lesson summary used in list endpoints."""

    id: uuid.UUID
    title: str
    dialect_segment: str
    level_band: str
    day_order: int
    # URL pointing to Object Storage — never a BLOB (Req 5.7)
    audio_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LessonDetailResponse(LessonResponse):
    """
    Full lesson detail including associated vocabulary items.
    Only vocabulary whose dialect_segment matches the lesson is returned (Req 3.3).
    """

    vocabulary: list[VocabularyItemResponse] = []
