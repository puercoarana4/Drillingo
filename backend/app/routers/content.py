from typing import Optional
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.schemas.content import LessonDetailResponse, LessonResponse, VocabularyItemResponse
from app.services.content_service import ContentService

router = APIRouter()

# Valid enum values for query param validation
VALID_DIALECTS = {"east_coast", "midwest"}
VALID_LEVELS = {"B1", "B2", "C1"}


@router.get(
    "/lessons",
    response_model=list[LessonResponse],
    summary="List lessons with optional dialect and level filters",
)
async def get_lessons(
    dialect: Optional[str] = Query(
        default=None,
        description="Filter by dialect: east_coast | midwest",
    ),
    level: Optional[str] = Query(
        default=None,
        description="Filter by CEFR level: B1 | B2 | C1",
    ),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """
    Return lessons filtered by dialect_segment and/or level_band.
    If no dialect is provided, lessons from both regions are returned ordered
    by day_order (Req 3.1, 3.2, 3.5).
    """
    service = ContentService(db)
    return await service.get_lessons(
        dialect=dialect if dialect in VALID_DIALECTS else None,
        level=level if level in VALID_LEVELS else None,
    )


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonDetailResponse,
    summary="Get full lesson detail including vocabulary",
)
async def get_lesson_detail(
    lesson_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """
    Return a single lesson with its associated vocabulary items.
    Only vocabulary whose dialect_segment matches the lesson is included (Req 3.3).
    """
    service = ContentService(db)
    return await service.get_lesson_detail(lesson_id)


@router.get(
    "/vocabulary",
    response_model=list[VocabularyItemResponse],
    summary="List vocabulary items with optional dialect and level filters",
)
async def get_vocabulary(
    dialect: Optional[str] = Query(
        default=None,
        description="Filter by dialect: east_coast | midwest",
    ),
    level: Optional[str] = Query(
        default=None,
        description="Filter by CEFR level: B1 | B2 | C1",
    ),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """
    Return vocabulary items filtered by dialect and/or level.
    dialect_segment is always present in each response item (Req 3.4).
    """
    service = ContentService(db)
    return await service.get_vocabulary(
        dialect=dialect if dialect in VALID_DIALECTS else None,
        level=level if level in VALID_LEVELS else None,
    )


@router.get(
    "/vocabulary/{item_id}",
    response_model=VocabularyItemResponse,
    summary="Get a single vocabulary item by ID",
)
async def get_vocabulary_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """Return a single vocabulary item including its dialect_segment (Req 3.4)."""
    from fastapi import HTTPException, status

    service = ContentService(db)
    items = await service.get_vocabulary()
    # Use repo directly for single-item lookup
    from app.repositories.vocabulary_repo import VocabularyRepository
    from app.schemas.content import VocabularyItemResponse

    repo = VocabularyRepository(db)
    item = await repo.get_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary item not found",
        )
    return VocabularyItemResponse.model_validate(item)
