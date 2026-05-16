"""
Property 3: Validación de scores fuera de rango
For any integer outside [0, 100], OralReportRequest raises ValidationError.

Feature: drillingo, Property 3: out-of-range scores rejected
Validates: Requirements 7.4
"""
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from app.schemas.report import OralReportRequest


@given(
    score=st.one_of(
        st.integers(max_value=-1),
        st.integers(min_value=101),
    )
)
@settings(max_examples=100)
def test_invalid_fluency_score_rejected(score: int):
    """
    Property 3a: Any fluency_score outside [0, 100] must raise ValidationError.
    """
    with pytest.raises(ValidationError):
        OralReportRequest(
            fluency_score=score,
            pronunciation_score=50,
            session_duration_seconds=600,
        )


@given(
    score=st.one_of(
        st.integers(max_value=-1),
        st.integers(min_value=101),
    )
)
@settings(max_examples=100)
def test_invalid_pronunciation_score_rejected(score: int):
    """
    Property 3b: Any pronunciation_score outside [0, 100] must raise ValidationError.
    """
    with pytest.raises(ValidationError):
        OralReportRequest(
            fluency_score=50,
            pronunciation_score=score,
            session_duration_seconds=600,
        )


@given(
    fluency=st.integers(min_value=0, max_value=100),
    pronunciation=st.integers(min_value=0, max_value=100),
)
@settings(max_examples=100)
def test_valid_scores_always_accepted(fluency: int, pronunciation: int):
    """
    Property 3c (inverse): Any score in [0, 100] must always be accepted.
    """
    req = OralReportRequest(
        fluency_score=fluency,
        pronunciation_score=pronunciation,
        session_duration_seconds=600,
    )
    assert 0 <= req.fluency_score <= 100
    assert 0 <= req.pronunciation_score <= 100
