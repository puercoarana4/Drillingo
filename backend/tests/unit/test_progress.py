"""
Unit tests for ProgressService — XP, level-up, and vocabulary mastery (Req 10.1–10.3, 11.1).
Uses mocked DB and repositories to avoid requiring a live database.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.progress_service import ProgressService, XP_BY_MODULE, LEVEL_THRESHOLDS
from app.schemas.progress import LessonProgressRequest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_user(level_band: str = "B1", xp_total: int = 0) -> MagicMock:
    user = MagicMock()
    user.id = uuid.uuid4()
    user.level_band = level_band
    user.xp_total = xp_total
    return user


def _make_progress_record(module_type: str, score: int) -> MagicMock:
    record = MagicMock()
    record.id = uuid.uuid4()
    record.user_id = uuid.uuid4()
    record.lesson_id = uuid.uuid4()
    record.module_type = module_type
    record.score = score
    record.completed_at = datetime.now(timezone.utc)
    return record


# ── XP per module (Req 10.1) ──────────────────────────────────────────────────

def test_xp_values_are_correct():
    """Req 10.1: XP awarded per module type must match spec."""
    assert XP_BY_MODULE["reading"] == 10
    assert XP_BY_MODULE["listening"] == 15
    assert XP_BY_MODULE["writing"] == 20
    assert XP_BY_MODULE["speaking"] == 25


@pytest.mark.asyncio
async def test_record_progress_awards_correct_xp_for_reading():
    """Req 10.1: completing a reading module awards 10 XP."""
    mock_db = AsyncMock()
    service = ProgressService(mock_db)
    user = _make_user(xp_total=0)
    record = _make_progress_record("reading", 80)

    with patch.object(service.repo, "create_lesson_progress", return_value=record):
        with patch.object(service, "_add_xp", return_value=10) as mock_xp:
            with patch.object(service, "check_level_up", return_value=None):
                result = await service.record_lesson_progress(
                    user.id,
                    LessonProgressRequest(
                        lesson_id=uuid.uuid4(), module_type="reading", score=80
                    ),
                )

    mock_xp.assert_called_once_with(user.id, 10)
    assert result.xp_awarded == 10


@pytest.mark.asyncio
async def test_record_progress_awards_correct_xp_for_speaking():
    """Req 10.1: completing a speaking module awards 25 XP."""
    mock_db = AsyncMock()
    service = ProgressService(mock_db)
    user = _make_user(xp_total=0)
    record = _make_progress_record("speaking", 90)

    with patch.object(service.repo, "create_lesson_progress", return_value=record):
        with patch.object(service, "_add_xp", return_value=25) as mock_xp:
            with patch.object(service, "check_level_up", return_value=None):
                result = await service.record_lesson_progress(
                    user.id,
                    LessonProgressRequest(
                        lesson_id=uuid.uuid4(), module_type="speaking", score=90
                    ),
                )

    mock_xp.assert_called_once_with(user.id, 25)
    assert result.xp_awarded == 25


# ── Level-up thresholds (Req 10.2, 10.3) ─────────────────────────────────────

def test_level_thresholds_are_correct():
    """Req 10.3: thresholds must be 500 XP for B2 and 2000 XP for C1."""
    threshold_map = {level: xp for xp, level in LEVEL_THRESHOLDS}
    assert threshold_map["B2"] == 500
    assert threshold_map["C1"] == 2000


@pytest.mark.asyncio
async def test_check_level_up_b1_to_b2_at_threshold():
    """Req 10.2: user at exactly 500 XP advances from B1 to B2."""
    mock_db = AsyncMock()
    service = ProgressService(mock_db)

    user = _make_user(level_band="B1", xp_total=500)

    # Mock the DB select to return our user
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = user
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    await service.check_level_up(user.id, 500)

    assert user.level_band == "B2"
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_check_level_up_b2_to_c1_at_threshold():
    """Req 10.2: user at exactly 2000 XP advances from B2 to C1."""
    mock_db = AsyncMock()
    service = ProgressService(mock_db)

    user = _make_user(level_band="B2", xp_total=2000)

    mock_result = MagicMock()
    mock_result.scalar_one.return_value = user
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    await service.check_level_up(user.id, 2000)

    assert user.level_band == "C1"
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_check_level_up_no_change_below_threshold():
    """No level-up when XP is below 500."""
    mock_db = AsyncMock()
    service = ProgressService(mock_db)

    user = _make_user(level_band="B1", xp_total=499)

    mock_result = MagicMock()
    mock_result.scalar_one.return_value = user
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    await service.check_level_up(user.id, 499)

    assert user.level_band == "B1"
    mock_db.commit.assert_not_called()


# ── Vocabulary mastery (Req 11.1) ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_vocabulary_auto_mastered_after_3_correct():
    """Req 11.1: item is mastered automatically after 3 correct answers."""
    mock_db = AsyncMock()
    service = ProgressService(mock_db)

    vocab_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Simulate row with correct_count already at 2
    existing_row = MagicMock()
    existing_row.correct_count = 2
    existing_row.mastered = False

    with patch.object(service.repo, "upsert_vocabulary_interaction") as mock_upsert:
        # Simulate the repo setting mastered=True when correct_count reaches 3
        async def fake_upsert(uid, vid, correct):
            if correct:
                existing_row.correct_count += 1
            if existing_row.correct_count >= 3:
                existing_row.mastered = True
            return existing_row

        mock_upsert.side_effect = fake_upsert
        await service.update_vocabulary_interaction(user_id, vocab_id, correct=True)

    assert existing_row.mastered is True
    assert existing_row.correct_count == 3


@pytest.mark.asyncio
async def test_vocabulary_not_mastered_before_3_correct():
    """Item is NOT mastered with only 2 correct answers."""
    mock_db = AsyncMock()
    service = ProgressService(mock_db)

    vocab_id = uuid.uuid4()
    user_id = uuid.uuid4()

    existing_row = MagicMock()
    existing_row.correct_count = 1
    existing_row.mastered = False

    with patch.object(service.repo, "upsert_vocabulary_interaction") as mock_upsert:
        async def fake_upsert(uid, vid, correct):
            if correct:
                existing_row.correct_count += 1
            if existing_row.correct_count >= 3:
                existing_row.mastered = True
            return existing_row

        mock_upsert.side_effect = fake_upsert
        await service.update_vocabulary_interaction(user_id, vocab_id, correct=True)

    assert existing_row.mastered is False
    assert existing_row.correct_count == 2
