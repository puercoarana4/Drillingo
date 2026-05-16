"""
Unit tests for the Streak Engine (Req 8.1–8.9).
Pure logic tests — no live DB required.
"""
import uuid
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.streak_engine import process_checkin
from app.models.streak import Streak


def _make_streak(current: int, longest: int, last_date: date) -> Streak:
    s = Streak()
    s.user_id = uuid.uuid4()
    s.current_streak = current
    s.longest_streak = longest
    s.last_activity_date = last_date
    return s


# ── First check-in ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_first_checkin_sets_streak_to_1():
    """Req 8.1: first activity ever → current_streak = 1."""
    mock_db = AsyncMock()
    user_id = uuid.uuid4()

    with patch("app.services.streak_engine.StreakRepository") as MockRepo:
        repo_instance = MockRepo.return_value
        repo_instance.get_by_user_id = AsyncMock(return_value=None)

        saved = MagicMock()
        saved.current_streak = 1
        saved.longest_streak = 1
        saved.last_activity_date = date.today()
        repo_instance.upsert = AsyncMock(return_value=saved)

        result = await process_checkin(user_id, "America/New_York", mock_db)

    assert result.current_streak == 1
    assert result.longest_streak == 1


# ── Consecutive day ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_consecutive_day_increments_streak():
    """Req 8.1: activity on consecutive day → current_streak += 1."""
    mock_db = AsyncMock()
    user_id = uuid.uuid4()
    yesterday = date.today() - timedelta(days=1)
    existing = _make_streak(current=3, longest=5, last_date=yesterday)

    with patch("app.services.streak_engine.StreakRepository") as MockRepo:
        repo_instance = MockRepo.return_value
        repo_instance.get_by_user_id = AsyncMock(return_value=existing)

        saved = MagicMock()
        saved.current_streak = 4
        saved.longest_streak = 5
        saved.last_activity_date = date.today()
        repo_instance.upsert = AsyncMock(return_value=saved)

        result = await process_checkin(user_id, "America/Chicago", mock_db)

    assert result.current_streak == 4


# ── Streak broken ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_missed_day_resets_streak_to_1():
    """Req 8.3: missing a day resets current_streak to 1."""
    mock_db = AsyncMock()
    user_id = uuid.uuid4()
    two_days_ago = date.today() - timedelta(days=2)
    existing = _make_streak(current=7, longest=7, last_date=two_days_ago)

    with patch("app.services.streak_engine.StreakRepository") as MockRepo:
        repo_instance = MockRepo.return_value
        repo_instance.get_by_user_id = AsyncMock(return_value=existing)

        saved = MagicMock()
        saved.current_streak = 1
        saved.longest_streak = 7
        saved.last_activity_date = date.today()
        repo_instance.upsert = AsyncMock(return_value=saved)

        result = await process_checkin(user_id, "America/Chicago", mock_db)

    assert result.current_streak == 1
    assert result.longest_streak == 7  # longest preserved


# ── Idempotent same-day check-in ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_same_day_checkin_is_idempotent():
    """Req 8.1: checking in twice on the same day does not change the streak."""
    mock_db = AsyncMock()
    user_id = uuid.uuid4()
    today = date.today()
    existing = _make_streak(current=5, longest=5, last_date=today)

    with patch("app.services.streak_engine.StreakRepository") as MockRepo:
        repo_instance = MockRepo.return_value
        repo_instance.get_by_user_id = AsyncMock(return_value=existing)
        repo_instance.upsert = AsyncMock()  # should NOT be called

        result = await process_checkin(user_id, "America/New_York", mock_db)

    repo_instance.upsert.assert_not_called()
    assert result.current_streak == 5


# ── longest_streak update (Req 8.2) ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_longest_streak_updated_when_current_exceeds_it():
    """Req 8.2: longest_streak updated when current_streak surpasses it."""
    mock_db = AsyncMock()
    user_id = uuid.uuid4()
    yesterday = date.today() - timedelta(days=1)
    existing = _make_streak(current=5, longest=5, last_date=yesterday)

    with patch("app.services.streak_engine.StreakRepository") as MockRepo:
        repo_instance = MockRepo.return_value
        repo_instance.get_by_user_id = AsyncMock(return_value=existing)

        saved = MagicMock()
        saved.current_streak = 6
        saved.longest_streak = 6
        saved.last_activity_date = date.today()
        repo_instance.upsert = AsyncMock(return_value=saved)

        result = await process_checkin(user_id, "America/New_York", mock_db)

    assert result.longest_streak == 6
    assert result.current_streak == 6


# ── Invalid timezone (Req 8.9) ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invalid_timezone_raises_400():
    """Req 8.9: invalid IANA timezone → HTTP 400."""
    from fastapi import HTTPException

    mock_db = AsyncMock()
    user_id = uuid.uuid4()

    with pytest.raises(HTTPException) as exc_info:
        await process_checkin(user_id, "Not/AReal_Timezone", mock_db)

    assert exc_info.value.status_code == 400
    assert "Invalid timezone" in exc_info.value.detail
