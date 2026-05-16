from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.schemas.streak import CheckinRequest, StreakResponse
from app.repositories.streak_repo import StreakRepository
from app.services.streak_engine import process_checkin

router = APIRouter()


@router.post(
    "/checkin",
    response_model=StreakResponse,
    summary="Daily check-in — updates streak using client timezone",
)
async def checkin(
    data: CheckinRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Process a daily check-in.
    The client must send its IANA timezone so the streak resets at local
    midnight, not the server's UTC midnight (Req 8.5, 8.9).
    """
    return await process_checkin(current_user.id, data.timezone, db)


@router.get(
    "",
    response_model=StreakResponse,
    summary="Get current streak state for the authenticated user",
)
async def get_streak(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return current_streak, longest_streak, and last_activity_date."""
    repo = StreakRepository(db)
    streak = await repo.get_by_user_id(current_user.id)
    if streak is None:
        return StreakResponse(current_streak=0, longest_streak=0, last_activity_date=None)
    return StreakResponse(
        current_streak=streak.current_streak,
        longest_streak=streak.longest_streak,
        last_activity_date=streak.last_activity_date,
    )
