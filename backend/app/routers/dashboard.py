from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import get_dashboard

router = APIRouter()


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Get all dashboard metrics in a single response",
)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return all dashboard metrics aggregated in parallel.
    Target response time: < 500ms (Req 9.5).
    Includes: level, XP, streak, radar scores, vocab count, oral history,
    level history.
    """
    return await get_dashboard(current_user.id, db)
