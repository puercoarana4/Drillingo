"""
Run seed against Railway production database directly.
"""
import asyncio
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ─── Override DATABASE_URL before importing seed logic ───
import os
RAILWAY_URL = "postgresql+asyncpg://postgres:kZFnTSCEceQoFcuXrpGXJUiDfnRxfWgB@metro.proxy.rlwy.net:39510/railway"
os.environ["DATABASE_URL"] = RAILWAY_URL.strip()

# ─── Reimport seed internals ─────────────────────────────
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import json
import uuid

engine = create_async_engine(RAILWAY_URL.strip(), echo=False, future=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

def _jdump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

# ── Paste exact VOCABULARY_ITEMS and ALL_LESSONS from seed.py ──
exec(open("seed.py", encoding="utf-8").read().split("async def _reset_content")[0].replace(
    "engine = create_async_engine(_build_async_url()", 
    "# engine = create_async_engine(_build_async_url()"
))

async def _reset_content(session):
    print("  Borrando lecciones existentes...")
    await session.execute(text("DELETE FROM lessons"))
    print("  Borrando vocabulario existente...")
    await session.execute(text("DELETE FROM vocabulary_items"))
    await session.commit()
    print("  Contenido previo eliminado.")

async def _seed_vocabulary(session):
    print(f"  Insertando {len(VOCABULARY_ITEMS)} terminos de vocabulario...")
    for item in VOCABULARY_ITEMS:
        await session.execute(
            text("""
                INSERT INTO vocabulary_items
                    (id, term, definition, example_sentence, dialect_segment, level_band)
                VALUES
                    (:id, :term, :definition, :example_sentence,
                     CAST(:dialect_segment AS dialect_segment_enum),
                     CAST(:level_band AS level_band_enum))
                ON CONFLICT (id) DO UPDATE SET
                    definition = EXCLUDED.definition
            """),
            {
                "id": str(item["id"]),
                "term": item["term"],
                "definition": item["definition"],
                "example_sentence": item.get("example_sentence", ""),
                "dialect_segment": item.get("dialect_segment", "midwest"),
                "level_band": "B1",
            },
        )
    await session.commit()
    print(f"  {len(VOCABULARY_ITEMS)} terminos insertados.")

async def _seed_lessons(session):
    print(f"  Insertando/actualizando {len(ALL_LESSONS)} lecciones...")
    for lesson in ALL_LESSONS:
        await session.execute(
            text("""
                INSERT INTO lessons
                    (id, title, dialect_segment, level_band, day_order, audio_url)
                VALUES
                    (:id, :title,
                     CAST(:dialect_segment AS dialect_segment_enum),
                     CAST(:level_band AS level_band_enum),
                     :day_order, :audio_url)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    audio_url = EXCLUDED.audio_url,
                    day_order = EXCLUDED.day_order
            """),
            {
                "id": str(lesson["id"]),
                "title": lesson["title"],
                "dialect_segment": lesson["dialect_segment"],
                "level_band": lesson["level_band"],
                "day_order": lesson["day_order"],
                "audio_url": lesson["audio_url"],
            },
        )
    await session.commit()
    print(f"  {len(ALL_LESSONS)} lecciones insertadas/actualizadas.")

async def main():
    print("\n[Drillingo] Seeding Railway production database...")
    async with SessionLocal() as session:
        await _reset_content(session)
        await _seed_vocabulary(session)
        await _seed_lessons(session)
        
        vocab_count = (await session.execute(text("SELECT COUNT(*) FROM vocabulary_items"))).scalar()
        lesson_count = (await session.execute(text("SELECT COUNT(*) FROM lessons"))).scalar()
        print(f"\n  vocabulary_items : {vocab_count}")
        print(f"  lessons          : {lesson_count}")
    print("\n[SUCCESS] Railway seed completado!\n")

asyncio.run(main())
