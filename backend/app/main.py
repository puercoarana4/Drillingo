from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers import auth, content, progress, streak, report, dashboard, ai

app = FastAPI(
    title="Drillingo API",
    version="0.1.0",
    description="Gamified English learning platform focused on AAVE and Drill culture.",
)

# CORS — allow Next.js frontend in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(streak.router, prefix="/api/streak", tags=["streak"])
app.include_router(report.router, prefix="/api/reports", tags=["reports"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/health/db", tags=["health"])
async def db_health(db: AsyncSession = Depends(get_db)):
    """DB health — shows lesson and vocab counts without auth."""
    from sqlalchemy import text
    lessons = (await db.execute(text("SELECT COUNT(*) FROM lessons"))).scalar()
    vocab = (await db.execute(text("SELECT COUNT(*) FROM vocabulary_items"))).scalar()
    return {"lessons": lessons, "vocabulary_items": vocab}
