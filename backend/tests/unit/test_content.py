"""
Unit tests for ContentService — dialect and level filtering (Req 3.1–3.6).
Uses mocked repositories to avoid requiring a live database.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.content_service import ContentService


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_lesson(dialect: str, level: str, day_order: int = 1) -> MagicMock:
    lesson = MagicMock()
    lesson.id = uuid.uuid4()
    lesson.title = f"Lesson {day_order}"
    lesson.dialect_segment = dialect
    lesson.level_band = level
    lesson.day_order = day_order
    lesson.audio_url = "https://s3.example.com/audio.mp3"
    lesson.created_at = datetime.now(timezone.utc)
    return lesson


def _make_vocab(dialect: str, level: str) -> MagicMock:
    item = MagicMock()
    item.id = uuid.uuid4()
    item.term = "finna"
    item.definition = "going to / about to"
    item.example_sentence = "I'm finna dip."
    item.dialect_segment = dialect
    item.level_band = level
    item.created_at = datetime.now(timezone.utc)
    return item


# ── get_lessons ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_lessons_no_filter_returns_all():
    """Req 3.5: no dialect → both regions returned."""
    mock_db = AsyncMock()
    service = ContentService(mock_db)

    lessons = [
        _make_lesson("east_coast", "B1", 1),
        _make_lesson("midwest", "B1", 2),
    ]
    with patch.object(service.lesson_repo, "find_by_dialect_and_level", return_value=lessons):
        result = await service.get_lessons()

    assert len(result) == 2
    dialects = {r.dialect_segment for r in result}
    assert dialects == {"east_coast", "midwest"}


@pytest.mark.asyncio
async def test_get_lessons_filter_by_dialect_east_coast():
    """Req 3.1: dialect=east_coast → only east_coast lessons returned."""
    mock_db = AsyncMock()
    service = ContentService(mock_db)

    lessons = [_make_lesson("east_coast", "B1", 1)]
    with patch.object(service.lesson_repo, "find_by_dialect_and_level", return_value=lessons) as mock_find:
        result = await service.get_lessons(dialect="east_coast")

    assert len(result) == 1
    assert result[0].dialect_segment == "east_coast"
    mock_find.assert_called_once_with("east_coast", None)


@pytest.mark.asyncio
async def test_get_lessons_filter_by_level():
    """Req 3.2: level=B2 → only B2 lessons returned."""
    mock_db = AsyncMock()
    service = ContentService(mock_db)

    lessons = [_make_lesson("midwest", "B2", 5)]
    with patch.object(service.lesson_repo, "find_by_dialect_and_level", return_value=lessons) as mock_find:
        result = await service.get_lessons(level="B2")

    assert len(result) == 1
    assert result[0].level_band == "B2"
    mock_find.assert_called_once_with(None, "B2")


@pytest.mark.asyncio
async def test_get_lessons_filter_by_dialect_and_level():
    """Req 3.1 + 3.2: both filters applied simultaneously."""
    mock_db = AsyncMock()
    service = ContentService(mock_db)

    lessons = [_make_lesson("east_coast", "C1", 10)]
    with patch.object(service.lesson_repo, "find_by_dialect_and_level", return_value=lessons) as mock_find:
        result = await service.get_lessons(dialect="east_coast", level="C1")

    assert len(result) == 1
    assert result[0].dialect_segment == "east_coast"
    assert result[0].level_band == "C1"
    mock_find.assert_called_once_with("east_coast", "C1")


# ── get_lesson_detail ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_lesson_detail_returns_matching_vocab():
    """Req 3.3: vocab returned must match lesson's dialect_segment."""
    mock_db = AsyncMock()
    service = ContentService(mock_db)

    lesson = _make_lesson("east_coast", "B1", 1)
    vocab = [_make_vocab("east_coast", "B1")]

    with patch.object(service.lesson_repo, "get_by_id", return_value=lesson):
        with patch.object(service.vocab_repo, "find_by_dialect_and_level", return_value=vocab) as mock_vocab:
            result = await service.get_lesson_detail(lesson.id)

    # Vocab repo called with lesson's dialect and level
    mock_vocab.assert_called_once_with(dialect="east_coast", level="B1")
    assert len(result.vocabulary) == 1
    assert result.vocabulary[0].dialect_segment == "east_coast"


@pytest.mark.asyncio
async def test_get_lesson_detail_not_found_raises_404():
    """Lesson not found → 404."""
    from fastapi import HTTPException

    mock_db = AsyncMock()
    service = ContentService(mock_db)

    with patch.object(service.lesson_repo, "get_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await service.get_lesson_detail(uuid.uuid4())

    assert exc_info.value.status_code == 404


# ── get_vocabulary ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_vocabulary_dialect_segment_always_present():
    """Req 3.4: dialect_segment always included in vocab responses."""
    mock_db = AsyncMock()
    service = ContentService(mock_db)

    items = [
        _make_vocab("east_coast", "B1"),
        _make_vocab("midwest", "B2"),
    ]
    with patch.object(service.vocab_repo, "find_by_dialect_and_level", return_value=items):
        result = await service.get_vocabulary()

    for item in result:
        assert item.dialect_segment is not None


@pytest.mark.asyncio
async def test_get_vocabulary_filter_by_dialect():
    """Req 3.3: vocab filtered by dialect returns only matching items."""
    mock_db = AsyncMock()
    service = ContentService(mock_db)

    items = [_make_vocab("midwest", "B1")]
    with patch.object(service.vocab_repo, "find_by_dialect_and_level", return_value=items) as mock_find:
        result = await service.get_vocabulary(dialect="midwest")

    assert all(r.dialect_segment == "midwest" for r in result)
    mock_find.assert_called_once_with("midwest", None)
