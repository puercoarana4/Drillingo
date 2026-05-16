"""
Unit tests for ReportParser and OralReportRequest schema (Req 7.1–7.6).
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from app.schemas.report import OralReportRequest
from app.services.report_parser import ReportParser


# ── Schema validation ─────────────────────────────────────────────────────────

def test_valid_payload_passes():
    """Valid payload creates OralReportRequest without error."""
    req = OralReportRequest(
        session_duration_seconds=1800,
        fluency_score=78,
        pronunciation_score=82,
    )
    assert req.fluency_score == 78
    assert req.pronunciation_score == 82


def test_missing_fluency_score_raises_422():
    """Req 7.3: missing fluency_score → ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        OralReportRequest(
            session_duration_seconds=600,
            pronunciation_score=70,
        )
    errors = exc_info.value.errors()
    fields = [e["loc"][0] for e in errors]
    assert "fluency_score" in fields


def test_missing_pronunciation_score_raises_422():
    """Req 7.3: missing pronunciation_score → ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        OralReportRequest(
            session_duration_seconds=600,
            fluency_score=70,
        )
    errors = exc_info.value.errors()
    fields = [e["loc"][0] for e in errors]
    assert "pronunciation_score" in fields


def test_fluency_score_above_100_raises_422():
    """Req 7.4: fluency_score > 100 → ValidationError."""
    with pytest.raises(ValidationError):
        OralReportRequest(
            session_duration_seconds=600,
            fluency_score=101,
            pronunciation_score=70,
        )


def test_fluency_score_below_0_raises_422():
    """Req 7.4: fluency_score < 0 → ValidationError."""
    with pytest.raises(ValidationError):
        OralReportRequest(
            session_duration_seconds=600,
            fluency_score=-1,
            pronunciation_score=70,
        )


def test_pronunciation_score_out_of_range_raises_422():
    """Req 7.4: pronunciation_score outside [0,100] → ValidationError."""
    with pytest.raises(ValidationError):
        OralReportRequest(
            session_duration_seconds=600,
            fluency_score=70,
            pronunciation_score=150,
        )


def test_boundary_scores_are_valid():
    """Scores of exactly 0 and 100 are valid."""
    req_min = OralReportRequest(
        session_duration_seconds=1,
        fluency_score=0,
        pronunciation_score=0,
    )
    req_max = OralReportRequest(
        session_duration_seconds=3600,
        fluency_score=100,
        pronunciation_score=100,
    )
    assert req_min.fluency_score == 0
    assert req_max.fluency_score == 100


def test_optional_notes_field():
    """notes field is optional."""
    req = OralReportRequest(
        session_duration_seconds=600,
        fluency_score=75,
        pronunciation_score=80,
        notes="Practiced Kay Flock verse",
    )
    assert req.notes == "Practiced Kay Flock verse"

    req_no_notes = OralReportRequest(
        session_duration_seconds=600,
        fluency_score=75,
        pronunciation_score=80,
    )
    assert req_no_notes.notes is None


# ── Service layer ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_parse_and_persist_stores_raw_json_unmodified():
    """Req 7.6: raw_json stored without modification."""
    mock_db = AsyncMock()
    parser = ReportParser(mock_db)
    user_id = uuid.uuid4()

    payload = OralReportRequest(
        session_duration_seconds=1800,
        fluency_score=78,
        pronunciation_score=82,
        notes="Test session",
    )

    saved_report = MagicMock()
    saved_report.id = uuid.uuid4()
    saved_report.user_id = user_id
    saved_report.fluency_score = 78
    saved_report.pronunciation_score = 82
    saved_report.session_duration_seconds = 1800
    saved_report.submitted_at = datetime.now(timezone.utc)

    with patch.object(parser.repo, "create", return_value=saved_report) as mock_create:
        result = await parser.parse_and_persist(user_id, payload)

    # Verify raw_json passed to repo contains all fields unmodified
    call_kwargs = mock_create.call_args.kwargs
    assert call_kwargs["raw_json"]["fluency_score"] == 78
    assert call_kwargs["raw_json"]["pronunciation_score"] == 82
    assert call_kwargs["raw_json"]["session_duration_seconds"] == 1800
    assert call_kwargs["raw_json"]["notes"] == "Test session"


@pytest.mark.asyncio
async def test_parse_and_persist_returns_correct_response():
    """Req 7.2: successful persist returns OralReportResponse with correct fields."""
    mock_db = AsyncMock()
    parser = ReportParser(mock_db)
    user_id = uuid.uuid4()

    payload = OralReportRequest(
        session_duration_seconds=900,
        fluency_score=65,
        pronunciation_score=70,
    )

    saved_report = MagicMock()
    saved_report.id = uuid.uuid4()
    saved_report.user_id = user_id
    saved_report.fluency_score = 65
    saved_report.pronunciation_score = 70
    saved_report.session_duration_seconds = 900
    saved_report.submitted_at = datetime.now(timezone.utc)

    with patch.object(parser.repo, "create", return_value=saved_report):
        result = await parser.parse_and_persist(user_id, payload)

    assert result.fluency_score == 65
    assert result.pronunciation_score == 70
    assert result.user_id == user_id
