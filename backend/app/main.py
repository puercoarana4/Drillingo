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


@app.post("/admin/seed-lessons", tags=["admin"])
async def seed_lessons(db: AsyncSession = Depends(get_db)):
    """
    Emergency endpoint: inserts the 2 seed lessons directly.
    Safe to call multiple times (upsert).
    """
    import json as _json
    from sqlalchemy import text

    lessons = _build_seed_lessons()
    inserted = 0
    errors = []
    for lesson in lessons:
        try:
            await db.execute(
                text("""
                    INSERT INTO lessons (id, title, dialect_segment, level_band, day_order, audio_url)
                    VALUES (
                        :id, :title,
                        CAST(:dialect_segment AS dialect_segment_enum),
                        CAST(:level_band AS level_band_enum),
                        :day_order, :audio_url
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        audio_url = EXCLUDED.audio_url,
                        day_order = EXCLUDED.day_order
                """),
                lesson,
            )
            inserted += 1
        except Exception as e:
            errors.append(str(e))
    await db.commit()
    return {"inserted": inserted, "errors": errors}


def _build_seed_lessons():
    import json as _json

    def jd(obj):
        return _json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

    ec = jd({
        "lesson_title": "East Coast Block",
        "dialect_focus": "East Coast / NYC",
        "modules": {
            "reading": {
                "module_type": "reading",
                "dialect_focus": "East Coast — DD Osama / Kay Flock",
                "raw_text": "yo wtw? idn what he talkin bout fr, wrd2my-mom he buggin smh",
                "formal_translation": "Hey, what's going on? I don't know what he is talking about, for real. I swear on my mother he is acting irrational, shaking my head.",
                "breakdown": [
                    {"abbr": "yo", "meaning": "Hey / informal greeting"},
                    {"abbr": "wtw", "meaning": "What's the word? / What's going on? (East Coast)"},
                    {"abbr": "idn", "meaning": "I don't know"},
                    {"abbr": "talkin bout", "meaning": "talking about (dropped -g, AAVE)"},
                    {"abbr": "fr", "meaning": "for real — intensifier"},
                    {"abbr": "wrd2my-mom", "meaning": "word to my mother — oath of truth"},
                    {"abbr": "buggin", "meaning": "acting irrationally"},
                    {"abbr": "smh", "meaning": "shaking my head — disappointment/disbelief"},
                ],
                "grammar_notes": [
                    "Dropped copula: 'he buggin' = 'he is bugging'.",
                    "'talkin bout' — -ing reduced to -in' in casual AAVE.",
                ],
                "cefr_target": "B1→B2",
                "xp_reward": 10,
            },
            "listening": {
                "module_type": "listening",
                "artist": "Kay Flock",
                "dialect_focus": "East Coast / NYC",
                "audio_s3_url": "https://drillingo-assets.s3.amazonaws.com/audio/kay_flock.mp3",
                "youtube_video_id": "Hy-tMDFBpgk",
                "original_bar": "Word to my mom, I ain't runnin' from no opp.",
                "exercise_text": "______ to my mom, I ______ runnin' from no opp.",
                "blanks": [
                    {"position": 1, "correct_answers": ["Word", "word"], "hint": "East Coast oath", "distractor_options": ["Word", "Swear", "True", "Real"]},
                    {"position": 2, "correct_answers": ["ain't", "aint"], "hint": "AAVE negation", "distractor_options": ["ain't", "won't", "don't", "can't"]},
                ],
                "full_translation": "I swear on my mother, I am not running away from any opponent.",
                "grammar_notes": ["Double negation: 'ain't' + 'no' = emphatic negation."],
                "cefr_target": "B1→B2",
                "xp_reward": 15,
            },
            "writing": {
                "module_type": "writing",
                "formal_input": "I do not have any money and I am not going to do that.",
                "expected_drill_output": "I ain't got no money and I ain't finna do allat",
                "accepted_variants": [
                    "I ain't got no money and I ain't finna do allat",
                    "I ain't got no money and I ain't finna do all that",
                    "Ain't got no money and ain't finna do allat",
                ],
                "evaluation_rubric": {
                    "double_negation": {"description": "Uses 'ain't' + 'no'", "points": 40, "example": "'ain't got no money' ✓"},
                    "finna_usage": {"description": "Uses 'finna' as future marker", "points": 30, "example": "'ain't finna do' ✓"},
                    "allat_compression": {"description": "Uses 'allat'", "points": 30, "example": "'allat' ✓"},
                },
                "grammar_explanation": "AAVE double negation is emphatic. 'Finna' replaces 'going to'. 'Allat' = 'all of that'.",
                "cefr_target": "B1→B2",
                "xp_reward": 20,
            },
        },
    })

    mw = jd({
        "lesson_title": "Midwest Block",
        "dialect_focus": "Midwest / Chicago",
        "modules": {
            "reading": {
                "module_type": "reading",
                "dialect_focus": "Midwest / Chicago — Lil Jeff / Bloodhound Q50",
                "raw_text": "wfs? slide to the block, we tryna see wtw, don't dodge",
                "formal_translation": "What's up? Come to the neighborhood, we are trying to find out what is going on. Do not avoid us.",
                "breakdown": [
                    {"abbr": "wfs", "meaning": "What's the fuck's up? (Chicago)"},
                    {"abbr": "slide", "meaning": "to come through / travel to a location"},
                    {"abbr": "block", "meaning": "the neighborhood block"},
                    {"abbr": "tryna", "meaning": "trying to (AAVE contraction)"},
                    {"abbr": "wtw", "meaning": "what's the word / what's happening"},
                    {"abbr": "dodge", "meaning": "to avoid, evade, or not show up"},
                ],
                "grammar_notes": [
                    "'tryna' = 'trying to' — AAVE contraction.",
                    "Imperative 'slide' — direct command register.",
                ],
                "cefr_target": "B1→B2",
                "xp_reward": 10,
            },
            "listening": {
                "module_type": "listening",
                "artist": "King Von",
                "dialect_focus": "Midwest / Chicago",
                "audio_s3_url": "https://drillingo-assets.s3.amazonaws.com/audio/king_von.mp3",
                "youtube_video_id": "RKnS5pDDMoI",
                "original_bar": "We finna slide, merch it on Von you ain't outside.",
                "exercise_text": "We ______ slide, ______ it on Von you ain't outside.",
                "blanks": [
                    {"position": 1, "correct_answers": ["finna"], "hint": "AAVE future marker", "distractor_options": ["gonna", "finna", "tryna", "bout to"]},
                    {"position": 2, "correct_answers": ["merch", "Merch"], "hint": "Chicago: put on a memorial shirt", "distractor_options": ["merch", "catch", "drop", "hit"]},
                ],
                "full_translation": "We are about to go confront them. I swear on King Von you are not in the streets.",
                "grammar_notes": ["'finna' replaces 'going to'.", "'merch it on Von' — oath using artist's name."],
                "cefr_target": "B1→B2",
                "xp_reward": 15,
            },
            "writing": {
                "module_type": "writing",
                "formal_input": "He is acting crazy, he does not know anyone here.",
                "expected_drill_output": "He trippin', he don't know nobody here",
                "accepted_variants": [
                    "He trippin', he don't know nobody here",
                    "He trippin he don't know nobody here",
                    "He buggin', he don't know nobody here",
                ],
                "evaluation_rubric": {
                    "dropped_copula": {"description": "Omits 'is' before 'trippin''", "points": 35, "example": "'He trippin'' ✓"},
                    "trippin_or_buggin": {"description": "Uses 'trippin'' or 'buggin''", "points": 25, "example": "'trippin'' ✓"},
                    "double_negation": {"description": "Uses 'don't know nobody'", "points": 40, "example": "'don't know nobody' ✓"},
                },
                "grammar_explanation": "Dropped copula: 'He trippin'' = 'He is acting crazy'. Double negation: 'don't know nobody' = emphatic.",
                "cefr_target": "B1→B2",
                "xp_reward": 20,
            },
        },
    })

    return [
        {"id": "55555555-0001-0001-0001-000000000001", "title": "Lesson 1 — East Coast Block (DD Osama / Kay Flock)", "dialect_segment": "east_coast", "level_band": "B1", "day_order": 1, "audio_url": ec},
        {"id": "55555555-0002-0002-0002-000000000002", "title": "Lesson 2 — Midwest Block (King Von / Lil Jeff)", "dialect_segment": "midwest", "level_band": "B1", "day_order": 2, "audio_url": mw},
    ]
