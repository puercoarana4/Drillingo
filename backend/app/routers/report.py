from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.schemas.report import OralReportRequest, OralReportResponse
from app.services.report_parser import ReportParser

router = APIRouter()


@router.post(
    "/oral",
    response_model=OralReportResponse,
    status_code=201,
    summary="Submit an oral practice session report",
)
async def submit_oral_report(
    payload: OralReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Accept a JSON report from an external oral practice session.
    - Returns 422 if fluency_score or pronunciation_score is outside [0, 100].
    - raw_json is stored as JSONB without modification (Req 7.6).
    """
    parser = ReportParser(db)
    return await parser.parse_and_persist(current_user.id, payload)


@router.get(
    "/oral",
    response_model=list[OralReportResponse],
    summary="Get oral report history for the current user",
)
async def get_oral_reports(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return the 30 most recent oral reports, newest first."""
    parser = ReportParser(db)
    return await parser.get_user_reports(current_user.id)
