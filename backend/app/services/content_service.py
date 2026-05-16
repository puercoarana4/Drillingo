import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson
from app.models.vocabulary import VocabularyItem
from app.repositories.lesson_repo import LessonRepository
from app.repositories.vocabulary_repo import VocabularyRepository
from app.schemas.content import LessonDetailResponse, LessonResponse, VocabularyItemResponse


class ContentService:
    def __init__(self, db: AsyncSession):
        self.lesson_repo = LessonRepository(db)
        self.vocab_repo = VocabularyRepository(db)

    async def get_lessons(
        self,
        dialect: Optional[str] = None,
        level: Optional[str] = None,
    ) -> list[LessonResponse]:
        """
        Return lessons filtered by dialect and/or level.
        If no dialect is provided, returns lessons from both regions ordered by
        day_order (Req 3.5).
        """
        lessons = await self.lesson_repo.find_by_dialect_and_level(dialect, level)
        return [LessonResponse.model_validate(l) for l in lessons]

    async def get_lesson_detail(
        self, lesson_id: uuid.UUID | str
    ) -> LessonDetailResponse:
        """
        Return full lesson detail including vocabulary items whose dialect_segment
        matches the lesson (Req 3.3).
        """
        lesson = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )

        # Only return vocab items matching the lesson's dialect (Req 3.3)
        vocab_items = await self.vocab_repo.find_by_dialect_and_level(
            dialect=lesson.dialect_segment,
            level=lesson.level_band,
        )

        vocab_responses = [VocabularyItemResponse.model_validate(v) for v in vocab_items]

        return LessonDetailResponse(
            id=lesson.id,
            title=lesson.title,
            dialect_segment=lesson.dialect_segment,
            level_band=lesson.level_band,
            day_order=lesson.day_order,
            audio_url=lesson.audio_url,
            created_at=lesson.created_at,
            vocabulary=vocab_responses,
        )

    async def get_vocabulary(
        self,
        dialect: Optional[str] = None,
        level: Optional[str] = None,
    ) -> list[VocabularyItemResponse]:
        """
        Return vocabulary items filtered by dialect and/or level.
        dialect_segment is always included in each response item (Req 3.4).
        """
        items = await self.vocab_repo.find_by_dialect_and_level(dialect, level)
        return [VocabularyItemResponse.model_validate(v) for v in items]
