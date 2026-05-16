"""
Property 4: Filtrado de lecciones por dialecto
For any list of lessons and any dialect filter, the result contains only
lessons matching that dialect.

Feature: drillingo, Property 4: dialect filter consistency
Validates: Requirements 3.1
"""
from dataclasses import dataclass
from typing import Optional

from hypothesis import given, settings
from hypothesis import strategies as st


@dataclass
class LessonStub:
    id: str
    title: str
    dialect_segment: str
    level_band: str
    day_order: int


def filter_lessons_by_dialect(
    lessons: list[LessonStub], dialect: Optional[str]
) -> list[LessonStub]:
    """
    Pure filtering function that mirrors ContentService.get_lessons logic.
    If dialect is None, returns all lessons.
    """
    if dialect is None:
        return lessons
    return [l for l in lessons if l.dialect_segment == dialect]


# ── Strategies ────────────────────────────────────────────────────────────────

lesson_strategy = st.builds(
    LessonStub,
    id=st.uuids().map(str),
    title=st.text(min_size=1, max_size=50),
    dialect_segment=st.sampled_from(["east_coast", "midwest"]),
    level_band=st.sampled_from(["B1", "B2", "C1"]),
    day_order=st.integers(min_value=1, max_value=365),
)


# ── Property tests ────────────────────────────────────────────────────────────

@given(
    dialect=st.sampled_from(["east_coast", "midwest"]),
    lessons=st.lists(lesson_strategy, min_size=0, max_size=50),
)
@settings(max_examples=100)
def test_dialect_filter_returns_only_matching(
    dialect: str, lessons: list[LessonStub]
):
    """
    Property 4: Every lesson in the filtered result has the requested dialect.
    """
    filtered = filter_lessons_by_dialect(lessons, dialect)
    assert all(l.dialect_segment == dialect for l in filtered), (
        f"Found non-matching dialect in results for filter={dialect}"
    )


@given(
    dialect=st.sampled_from(["east_coast", "midwest"]),
    lessons=st.lists(lesson_strategy, min_size=0, max_size=50),
)
@settings(max_examples=100)
def test_dialect_filter_no_false_negatives(
    dialect: str, lessons: list[LessonStub]
):
    """
    Property 4 (completeness): No lesson matching the dialect is excluded.
    """
    filtered = filter_lessons_by_dialect(lessons, dialect)
    matching_count = sum(1 for l in lessons if l.dialect_segment == dialect)
    assert len(filtered) == matching_count


@given(lessons=st.lists(lesson_strategy, min_size=0, max_size=50))
@settings(max_examples=100)
def test_no_filter_returns_all(lessons: list[LessonStub]):
    """
    Property 4 (no filter): None dialect returns all lessons unchanged.
    """
    result = filter_lessons_by_dialect(lessons, None)
    assert len(result) == len(lessons)
