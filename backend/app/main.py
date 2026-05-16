from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, content, progress, streak, report, dashboard

app = FastAPI(
    title="Drillingo API",
    version="0.1.0",
    description="Gamified English learning platform focused on AAVE and Drill culture.",
)

# CORS — allow Next.js frontend in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
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


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
