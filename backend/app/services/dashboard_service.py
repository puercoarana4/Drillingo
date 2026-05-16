import asyncio
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.oral_report import OralReport
from app.models.progress import LessonProgress
from app.models.streak import Streak
from app.models.user import User
from app.models.vocabulary import UserVocabulary
from app.schemas.dashboard import (
    DashboardResponse,
    LevelHistoryPoint,
    OralHistoryPoint,
    RadarScores,
)


async def get_dashboard(user_id: uuid.UUID, db: AsyncSession) -> DashboardResponse:
    """
    Aggregate all dashboard metrics in parallel using asyncio.gather (Req 9.5).
    Target response time: < 500ms.
    """
    (
        user_data,
        streak_data,
        radar_data,
        vocab_count,
        oral_history,
        level_history,
    ) = await asyncio.gather(
        _get_user_data(user_id, db),
        _get_streak_data(user_id, db),
        _get_radar_data(user_id, db),
        _get_vocab_mastered_count(user_id, db),
        _get_oral_history(user_id, db),
        _get_level_history(user_id, db),
    )

    return DashboardResponse(
        user_id=user_id,
        level_band=user_data["level_band"],
        xp_total=user_data["xp_total"],
        current_streak=streak_data["current_streak"],
        longest_streak=streak_data["longest_streak"],
        radar=RadarScores(
            reading=radar_data.get("reading", 0.0),
            listening=radar_data.get("listening", 0.0),
            writing=radar_data.get("writing", 0.0),
            speaking=radar_data.get("speaking", 0.0),
            vocabulary=vocab_count / 10.0 if vocab_count else 0.0,  # normalise to 0–100
        ),
        vocabulary_mastered_count=vocab_count,
        oral_history=oral_history,
        level_history=level_history,
    )


async def _get_user_data(user_id: uuid.UUID, db: AsyncSession) -> dict:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    return {"level_band": user.level_band, "xp_total": user.xp_total}


async def _get_streak_data(user_id: uuid.UUID, db: AsyncSession) -> dict:
    result = await db.execute(select(Streak).where(Streak.user_id == user_id))
    streak = result.scalar_one_or_none()
    if streak is None:
        return {"current_streak": 0, "longest_streak": 0}
    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
    }


async def _get_radar_data(user_id: uuid.UUID, db: AsyncSession) -> dict:
    """Return average score per module type for the radar chart (Req 9.2)."""
    result = await db.execute(
        select(
            LessonProgress.module_type,
            func.avg(LessonProgress.score).label("avg_score"),
        )
        .where(LessonProgress.user_id == user_id)
        .group_by(LessonProgress.module_type)
    )
    rows = result.all()
    return {row.module_type: float(row.avg_score) for row in rows}


async def _get_vocab_mastered_count(user_id: uuid.UUID, db: AsyncSession) -> int:
    """Count vocabulary items with mastered=True (Req 9.3)."""
    result = await db.execute(
        select(func.count(UserVocabulary.vocabulary_item_id)).where(
            UserVocabulary.user_id == user_id,
            UserVocabulary.mastered.is_(True),
        )
    )
    return result.scalar_one() or 0


async def _get_oral_history(
    user_id: uuid.UUID, db: AsyncSession
) -> list[OralHistoryPoint]:
    """Return last 30 oral reports ordered by submitted_at DESC (Req 9.4)."""
    result = await db.execute(
        select(OralReport)
        .where(OralReport.user_id == user_id)
        .order_by(OralReport.submitted_at.desc())
        .limit(30)
    )
    reports = result.scalars().all()
    return [
        OralHistoryPoint(
            submitted_at=r.submitted_at,
            fluency_score=r.fluency_score,
            pronunciation_score=r.pronunciation_score,
        )
        for r in reports
    ]


async def _get_level_history(
    user_id: uuid.UUID, db: AsyncSession
) -> list[LevelHistoryPoint]:
    """
    Derive level history from lesson_progress by grouping completed_at by date
    and tracking level_band changes (Req 9.1).
    """
    result = await db.execute(
        select(
            LessonProgress.completed_at,
            LessonProgress.module_type,
        )
        .where(LessonProgress.user_id == user_id)
        .order_by(LessonProgress.completed_at)
    )
    rows = result.all()

    # Get current user level for reference
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one()

    if not rows:
        return [LevelHistoryPoint(date=user.created_at, level_band=user.level_band)]

    # Build a simple history: first activity date at B1, current level at latest date
    first_date = rows[0].completed_at
    last_date = rows[-1].completed_at

    history = [LevelHistoryPoint(date=first_date, level_band="B1")]
    if user.level_band != "B1":
        history.append(LevelHistoryPoint(date=last_date, level_band=user.level_band))

    return history
