import uuid
from datetime import datetime, timedelta

import pytz
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.streak import Streak
from app.repositories.streak_repo import StreakRepository
from app.schemas.streak import StreakResponse


async def process_checkin(
    user_id: uuid.UUID,
    client_timezone: str,
    db: AsyncSession,
) -> StreakResponse:
    """
    Process a daily check-in for the given user.

    Uses the client's IANA timezone to determine the current calendar day,
    so the streak resets at the user's local midnight — not the server's UTC
    midnight (Req 8.5, 8.8, 8.9).

    Four cases:
    1. First activity ever → streak = 1
    2. Already checked in today → idempotent, no change
    3. Consecutive day → streak += 1
    4. Missed a day → streak resets to 1
    """
    # Validate timezone (Req 8.9) — schema already validates, but guard here too
    try:
        tz = pytz.timezone(client_timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid timezone: {client_timezone}",
        )

    # Current date in the client's local timezone (Req 8.5)
    today_client = datetime.now(tz).date()

    repo = StreakRepository(db)
    streak = await repo.get_by_user_id(user_id)

    if streak is None:
        # Case 1: First activity ever
        streak = Streak(
            user_id=user_id,
            current_streak=1,
            longest_streak=1,
            last_activity_date=today_client,
        )
    elif streak.last_activity_date == today_client:
        # Case 2: Already checked in today — idempotent
        return StreakResponse(
            current_streak=streak.current_streak,
            longest_streak=streak.longest_streak,
            last_activity_date=streak.last_activity_date,
        )
    elif streak.last_activity_date == today_client - timedelta(days=1):
        # Case 3: Consecutive day
        streak.current_streak += 1
        streak.last_activity_date = today_client
    else:
        # Case 4: Missed one or more days — reset streak
        streak.current_streak = 1
        streak.last_activity_date = today_client

    # Update longest_streak if current surpasses it (Req 8.2)
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak

    streak = await repo.upsert(streak)

    return StreakResponse(
        current_streak=streak.current_streak,
        longest_streak=streak.longest_streak,
        last_activity_date=streak.last_activity_date,
    )
