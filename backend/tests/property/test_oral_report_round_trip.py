"""
Property 1: Round-trip de Oral Report
For any valid OralReportRequest payload, parsing and re-serialising produces
a semantically equivalent object.

Feature: drillingo, Property 1: oral report JSON round-trip
Validates: Requirements 7.7
"""
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from app.schemas.report import OralReportRequest


@given(
    fluency_score=st.integers(min_value=0, max_value=100),
    pronunciation_score=st.integers(min_value=0, max_value=100),
    session_duration_seconds=st.integers(min_value=1, max_value=86400),
    notes=st.one_of(st.none(), st.text(max_size=500)),
)
@settings(max_examples=100)
def test_oral_report_round_trip(
    fluency_score: int,
    pronunciation_score: int,
    session_duration_seconds: int,
    notes,
):
    """
    Property 1: Parsing a valid OralReportRequest and serialising it back
    produces an object semantically equivalent to the original.
    """
    payload = {
        "fluency_score": fluency_score,
        "pronunciation_score": pronunciation_score,
        "session_duration_seconds": session_duration_seconds,
    }
    if notes is not None:
        payload["notes"] = notes

    # Parse
    parsed = OralReportRequest(**payload)
    # Serialise
    serialised = parsed.model_dump(exclude_none=True)
    # Re-parse
    re_parsed = OralReportRequest(**serialised)

    # Semantic equivalence
    assert re_parsed.fluency_score == parsed.fluency_score
    assert re_parsed.pronunciation_score == parsed.pronunciation_score
    assert re_parsed.session_duration_seconds == parsed.session_duration_seconds
    assert re_parsed.notes == parsed.notes
