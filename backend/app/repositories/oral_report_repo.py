import uuid
from typing import Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.oral_report import OralReport


class OralReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        raw_json: dict,
        fluency_score: int,
        pronunciation_score: int,
        session_duration_seconds: Optional[int],
    ) -> OralReport:
        """Persist a new oral report. raw_json stored as JSONB without modification."""
        report = OralReport(
            user_id=user_id,
            raw_json=raw_json,
            fluency_score=fluency_score,
            pronunciation_score=pronunciation_score,
            session_duration_seconds=session_duration_seconds,
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_by_user(
        self, user_id: uuid.UUID, limit: int = 30
    ) -> list[OralReport]:
        """Return the most recent oral reports for a user, newest first."""
        result = await self.db.execute(
            select(OralReport)
            .where(OralReport.user_id == user_id)
            .order_by(OralReport.submitted_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def query_by_jsonb(
        self, user_id: uuid.UUID, condition: str
    ) -> list[OralReport]:
        """
        Execute a raw JSONB filter query on oral_reports.
        Enables direct SQL queries like: raw_json->>'pronunciation_score' < '70'
        (Req 2.9, 2.10).

        Example condition: "CAST(raw_json->>'pronunciation_score' AS INTEGER) < 70"
        """
        stmt = text(
            f"SELECT * FROM oral_reports WHERE user_id = :uid AND {condition} "
            f"ORDER BY submitted_at DESC"
        )
        result = await self.db.execute(stmt, {"uid": str(user_id)})
        rows = result.mappings().all()
        # Re-query via ORM to get proper model instances
        ids = [row["id"] for row in rows]
        if not ids:
            return []
        orm_result = await self.db.execute(
            select(OralReport).where(OralReport.id.in_(ids))
        )
        return list(orm_result.scalars().all())
