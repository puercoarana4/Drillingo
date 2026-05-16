import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.schemas.progress import (
    LessonProgressRequest,
    LessonProgressResponse,
    LessonModuleProgressResponse,
    ProgressSummaryResponse,
    VocabularyProgressResponse,
)
from app.services.progress_service import ProgressService

router = APIRouter()


@router.post(
    "/lesson",
    response_model=LessonProgressResponse,
    status_code=201,
    summary="Record a completed lesson module and award XP",
)
async def record_lesson_progress(
    data: LessonProgressRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Persist a completed module (reading/listening/writing/speaking),
    award XP, and trigger level-up if threshold is crossed (Req 10.1–10.3).
    """
    service = ProgressService(db)
    return await service.record_lesson_progress(current_user.id, data)


@router.get(
    "/lessons",
    response_model=list[LessonModuleProgressResponse],
    summary="Get per-lesson module completion for the current user",
)
async def get_lessons_progress(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return a flat list of completed lesson+module combinations.
    Used by the learning path to determine which nodes are unlocked.
    """
    service = ProgressService(db)
    return await service.get_lessons_progress(current_user.id)


@router.get(
    "/summary",
    response_model=ProgressSummaryResponse,
    summary="Get aggregated progress summary for the current user",
)
async def get_progress_summary(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return level, XP, and per-module average scores."""
    service = ProgressService(db)
    return await service.get_progress_summary(current_user.id)


@router.get(
    "/vocabulary",
    response_model=list[VocabularyProgressResponse],
    summary="Get vocabulary progress for the current user",
)
async def get_vocabulary_progress(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return all vocabulary items the user has interacted with,
    including mastered status and correct_count (Req 11.2, 11.3).
    """
    service = ProgressService(db)
    return await service.get_vocabulary_progress(current_user.id)


@router.patch(
    "/vocabulary/{item_id}",
    status_code=204,
    summary="Record a vocabulary interaction (correct or incorrect)",
)
async def update_vocabulary_interaction(
    item_id: uuid.UUID,
    correct: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update correct_count and last_reviewed_at for a vocabulary item.
    Auto-masters the item after 3 correct answers (Req 11.1, 11.4).
    """
    service = ProgressService(db)
    await service.update_vocabulary_interaction(current_user.id, item_id, correct)
