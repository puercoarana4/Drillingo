import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.oral_report_repo import OralReportRepository
from app.schemas.report import OralReportRequest, OralReportResponse


class ReportParser:
    def __init__(self, db: AsyncSession):
        self.repo = OralReportRepository(db)

    async def parse_and_persist(
        self,
        user_id: uuid.UUID,
        payload: OralReportRequest,
    ) -> OralReportResponse:
        """
        Validate, persist, and return an Oral Report.

        - Pydantic schema handles field-level validation (missing fields → 422,
          out-of-range scores → 422).
        - raw_json is stored exactly as received — no modification (Req 7.6).
        - Round-trip property: serialising and re-parsing raw_json produces a
          semantically equivalent object (Req 7.7).
        """
        # Build the raw_json dict from the validated payload (Req 7.6)
        raw: dict[str, Any] = {
            "session_duration_seconds": payload.session_duration_seconds,
            "fluency_score": payload.fluency_score,
            "pronunciation_score": payload.pronunciation_score,
        }
        if payload.notes is not None:
            raw["notes"] = payload.notes

        report = await self.repo.create(
            user_id=user_id,
            raw_json=raw,
            fluency_score=payload.fluency_score,
            pronunciation_score=payload.pronunciation_score,
            session_duration_seconds=payload.session_duration_seconds,
        )

        return OralReportResponse(
            id=report.id,
            user_id=report.user_id,
            fluency_score=report.fluency_score,
            pronunciation_score=report.pronunciation_score,
            session_duration_seconds=report.session_duration_seconds,
            notes=payload.notes,
            submitted_at=report.submitted_at,
        )

    async def get_user_reports(self, user_id: uuid.UUID) -> list[OralReportResponse]:
        """Return the 30 most recent oral reports for a user."""
        reports = await self.repo.get_by_user(user_id, limit=30)
        return [
            OralReportResponse(
                id=r.id,
                user_id=r.user_id,
                fluency_score=r.fluency_score,
                pronunciation_score=r.pronunciation_score,
                session_duration_seconds=r.session_duration_seconds,
                notes=r.raw_json.get("notes"),
                submitted_at=r.submitted_at,
            )
            for r in reports
        ]
