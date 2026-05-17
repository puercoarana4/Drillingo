"""
seed.py — Drillingo Database Seeder
====================================
Cada lección contiene los 3 módulos (reading, listening, writing) en su payload.
El campo audio_url almacena un JSON con la clave "modules" que contiene los 3.

Uso:
    cd backend
    python seed.py           # inserta (skip si ya existe)
    python seed.py --reset   # borra y re-inserta
"""

import asyncio
import json
import os
import sys
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


def _build_async_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DATABASE_URL="):
                        url = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not url:
        raise RuntimeError("DATABASE_URL no está definida.")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


engine = create_async_engine(_build_async_url(), echo=False, future=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def _jdump(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


# ── VOCABULARY ────────────────────────────────────────────────────────────────

VOCABULARY_ITEMS = [
    {
        "id": uuid.UUID("11111111-0001-0001-0001-000000000001"),
        "term": "Buggin'",
        "definition": (
            "Acting erratically or irrationally. Derived from 'bugging out'. "
            "Core East Coast AAVE. Dropped copula: 'He buggin'' = 'He is bugging out'."
        ),
        "example_sentence": "Wrd2my-mom he buggin smh — I swear on my mother he is acting irrational.",
        "dialect_segment": "east_coast",
        "level_band": "B1",
    },
    {
        "id": uuid.UUID("11111111-0002-0002-0002-000000000002"),
        "term": "Merch it",
        "definition": (
            "To kill someone — 'put them on a shirt' (memorial t-shirts). "
            "Midwest/Chicago drill. C1: euphemistic nominalization of lethal violence."
        ),
        "example_sentence": "Merch it on Von you ain't outside — I swear on Von you are not in the streets.",
        "dialect_segment": "midwest",
        "level_band": "C1",
    },
    {
        "id": uuid.UUID("11111111-0003-0003-0003-000000000003"),
        "term": "Finna",
        "definition": (
            "Contracted 'fixing to' — immediate future intent. AAVE equivalent of 'going to'. "
            "Never co-occurs with 'be': 'I finna go' NOT 'I am finna go'."
        ),
        "example_sentence": "We finna slide — We are about to go confront them.",
        "dialect_segment": None,
        "level_band": "B1",
    },
    {
        "id": uuid.UUID("11111111-0004-0004-0004-000000000004"),
        "term": "Opp",
        "definition": (
            "Short for 'opponent/opposition'. Active rival or enemy. "
            "Double negation: 'ain't runnin from no opp' = emphatic 'not running from any opponent'."
        ),
        "example_sentence": "I ain't runnin from no opp — I am not running away from any opponent.",
        "dialect_segment": "east_coast",
        "level_band": "B2",
    },
    {
        "id": uuid.UUID("11111111-0005-0005-0005-000000000005"),
        "term": "Deadass",
        "definition": (
            "Adverb: 'seriously', 'for real'. East Coast AAVE, NYC-associated. "
            "Sentence-initial intensifier stronger than 'literally'."
        ),
        "example_sentence": "Deadass he don't know nobody on this block — Seriously, he does not know anyone here.",
        "dialect_segment": "east_coast",
        "level_band": "B2",
    },
    {
        "id": uuid.UUID("11111111-0006-0006-0006-000000000006"),
        "term": "Backdoor",
        "definition": (
            "To betray from within while pretending to be an ally. "
            "Chicago/Midwest drill. C1: premeditated deception by a trusted associate."
        ),
        "example_sentence": "They backdoored him, he thought they was solid — They betrayed him; he believed they were trustworthy.",
        "dialect_segment": "midwest",
        "level_band": "C1",
    },
]

# ── LESSONS — Each lesson has all 3 modules in its payload ────────────────────
#
# Structure stored in audio_url:
# {
#   "lesson_title": "...",
#   "dialect_focus": "...",
#   "modules": {
#     "reading": { ...reading payload... },
#     "listening": { ...listening payload... },
#     "writing": { ...writing payload... }
#   }
# }

_LESSON_EC_PAYLOAD = _jdump({
    "lesson_title": "East Coast Block — DD Osama / Kay Flock",
    "dialect_focus": "East Coast / NYC",
    "modules": {
        "reading": {
            "module_type": "reading",
            "dialect_focus": "East Coast — DD Osama / Kay Flock",
            "raw_text": "yo wtw? idn what he talkin bout fr, wrd2my-mom he buggin smh",
            "formal_translation": (
                "Hey, what's going on? I don't know what he is talking about, "
                "for real. I swear on my mother he is acting irrational, shaking my head."
            ),
            "breakdown": [
                {"abbr": "yo",          "meaning": "Hey / informal greeting"},
                {"abbr": "wtw",         "meaning": "What's the word? / What's going on? (East Coast)"},
                {"abbr": "idn",         "meaning": "I don't know"},
                {"abbr": "talkin bout", "meaning": "talking about (dropped -g, AAVE)"},
                {"abbr": "fr",          "meaning": "for real — intensifier"},
                {"abbr": "wrd2my-mom",  "meaning": "word to my mother — oath of truth"},
                {"abbr": "buggin",      "meaning": "acting irrationally (see vocab: Buggin')"},
                {"abbr": "smh",         "meaning": "shaking my head — disappointment/disbelief"},
            ],
            "grammar_notes": [
                "Dropped copula: 'he buggin' = 'he is bugging' — AAVE omits 'is' in present progressive.",
                "'talkin bout' — -ing reduced to -in' in casual AAVE speech.",
                "No punctuation except '?' — mirrors real DM/text register.",
            ],
            "cefr_target": "B1→B2",
            "xp_reward": 10,
        },
        "listening": {
            "module_type": "listening",
            "artist": "Kay Flock",
            "dialect_focus": "East Coast / NYC",
            "audio_s3_url": "https://drillingo-assets.s3.amazonaws.com/audio/kay_flock_word_to_my_mom.mp3",
            "youtube_video_id": "gGJS8W9emac",
            "original_bar": "Word to my mom, I ain't runnin' from no opp.",
            "exercise_text": "______ to my mom, I ______ runnin' from no opp.",
            "blanks": [
                {
                    "position": 1,
                    "correct_answers": ["Word", "word"],
                    "hint": "East Coast oath / truth affirmation",
                    "distractor_options": ["Word", "Swear", "True", "Real"],
                },
                {
                    "position": 2,
                    "correct_answers": ["ain't", "aint"],
                    "hint": "AAVE negation of 'am not' / 'is not' / 'are not'",
                    "distractor_options": ["ain't", "won't", "don't", "can't"],
                },
            ],
            "full_translation": "I swear on my mother, I am not running away from any opponent.",
            "grammar_notes": [
                "'Word to my mom' — East Coast oath, equivalent to 'I swear on my mother'.",
                "'ain't runnin'' — 'ain't' + present participle = emphatic present progressive negation.",
                "Double negation: 'ain't' + 'no' = emphatic 'not from any opponent'.",
            ],
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
                "I ain't got no bread and I ain't finna do allat",
            ],
            "evaluation_rubric": {
                "double_negation": {
                    "description": "Uses 'ain't' + 'no' for emphatic negation",
                    "points": 30,
                    "example": "'ain't got no money' ✓ — 'don't have any money' ✗",
                },
                "dropped_copula": {
                    "description": "Uses 'ain't finna' — drops 'am' before 'not going to'",
                    "points": 30,
                    "example": "'ain't finna do' ✓ — 'am not going to do' ✗",
                },
                "finna_usage": {
                    "description": "Replaces 'going to' with 'finna'",
                    "points": 20,
                    "example": "'finna do' ✓ — 'gonna do' partial credit",
                },
                "allat_compression": {
                    "description": "Compresses 'all of that' to 'allat' (C1 bonus)",
                    "points": 20,
                    "example": "'allat' ✓ — 'all that' partial credit",
                },
            },
            "grammar_explanation": (
                "AAVE double negation: 'ain't got no' is emphatic and grammatically correct. "
                "'Finna' replaces 'going to' entirely — never say 'am finna'. "
                "'Allat' = phonological compression of 'all of that'."
            ),
            "cefr_target": "B1→B2",
            "xp_reward": 20,
        },
        "speaking": {
            "module_type": "speaking",
            "target_phrase": "Word to my mom, I ain't runnin' from no opp.",
            "phonetic_tips": [
                "'Word to my mom' — stress on 'Word', drop the 'g' in running → 'runnin'",
                "'ain't' — contract fully, sounds like 'eynt' not 'am not'",
                "'no opp' — 'no' is unstressed, 'opp' gets the stress",
                "Rhythm: speak in a flow — match Kay Flock's cadence",
            ],
            "cefr_target": "B1→B2",
            "xp_reward": 25,
        },
    },
})

_LESSON_MW_PAYLOAD = _jdump({
    "lesson_title": "Midwest Block — King Von / Lil Jeff",
    "dialect_focus": "Midwest / Chicago",
    "modules": {
        "reading": {
            "module_type": "reading",
            "dialect_focus": "Midwest / Chicago — Lil Jeff / Bloodhound Q50",
            "raw_text": "wfs? slide to the block, we tryna see wtw, don't dodge",
            "formal_translation": (
                "What's up? Come to the neighborhood, we are trying to find out "
                "what is going on. Do not avoid us."
            ),
            "breakdown": [
                {"abbr": "wfs",   "meaning": "What's the fuck's up? / What's going on? (Chicago)"},
                {"abbr": "slide", "meaning": "to come through / travel to a location (Midwest drill)"},
                {"abbr": "block", "meaning": "the neighborhood block where the crew hangs"},
                {"abbr": "tryna", "meaning": "trying to (contracted, AAVE)"},
                {"abbr": "wtw",   "meaning": "what's the word / what's happening"},
                {"abbr": "dodge", "meaning": "to avoid, evade, or not show up (Chicago slang)"},
            ],
            "grammar_notes": [
                "'tryna' = 'trying to' — AAVE contraction, modal-like future intent.",
                "Imperative 'slide' — no subject, direct command register.",
                "Chicago drill texts omit punctuation and use minimal capitalization.",
            ],
            "cefr_target": "B1→B2",
            "xp_reward": 10,
        },
        "listening": {
            "module_type": "listening",
            "artist": "King Von",
            "dialect_focus": "Midwest / Chicago",
            "audio_s3_url": "https://drillingo-assets.s3.amazonaws.com/audio/king_von_finna_slide.mp3",
            "youtube_video_id": "g0v7Ow6Epog",
            "original_bar": "We finna slide, merch it on Von you ain't outside.",
            "exercise_text": "We ______ slide, ______ it on Von you ain't outside.",
            "blanks": [
                {
                    "position": 1,
                    "correct_answers": ["finna"],
                    "hint": "AAVE future marker meaning 'about to' / 'going to'",
                    "distractor_options": ["gonna", "finna", "tryna", "bout to"],
                },
                {
                    "position": 2,
                    "correct_answers": ["merch", "Merch"],
                    "hint": "Chicago slang: to put someone on a memorial t-shirt",
                    "distractor_options": ["merch", "catch", "drop", "hit"],
                },
            ],
            "full_translation": (
                "We are about to go confront them. I swear on King Von "
                "you are not actually in the streets."
            ),
            "grammar_notes": [
                "'finna slide' — 'finna' replaces 'going to'; 'slide' = travel to confront.",
                "'merch it on Von' — oath using a deceased artist's name as truth marker.",
                "'you ain't outside' — 'ain't' = 'are not'; 'outside' = active in the streets.",
            ],
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
                "He trippin', he don't know nobody out here",
                "He buggin', he don't know nobody here",
            ],
            "evaluation_rubric": {
                "dropped_copula": {
                    "description": "Omits 'is' before 'trippin'' — AAVE present progressive without copula",
                    "points": 35,
                    "example": "'He trippin'' ✓ — 'He is trippin'' ✗ (too formal)",
                },
                "trippin_or_buggin": {
                    "description": "Uses 'trippin'' or 'buggin'' instead of 'acting crazy'",
                    "points": 25,
                    "example": "'trippin'' ✓ — 'acting crazy' ✗",
                },
                "double_negation": {
                    "description": "Uses 'don't know nobody' — double negation for emphasis",
                    "points": 40,
                    "example": "'don't know nobody' ✓ — 'doesn't know anyone' ✗",
                },
            },
            "grammar_explanation": (
                "Dropped copula: 'He trippin'' = 'He is tripping/acting crazy'. "
                "Double negation: 'don't know nobody' = emphatic 'does not know anyone'. "
                "'don't' is used for all persons in AAVE — no third-person -s."
            ),
            "cefr_target": "B1→B2",
            "xp_reward": 20,
        },
        "speaking": {
            "module_type": "speaking",
            "target_phrase": "We finna slide, merch it on Von you ain't outside.",
            "phonetic_tips": [
                "'finna' — one fluid word, not 'fixing to'. Short 'i', unstressed",
                "'slide' — elongate slightly, Chicago drawl on the vowel",
                "'merch it' — stress on 'merch', 'it' is quick and unstressed",
                "'ain't outside' — 'ain't' contracted hard, stress on 'out' in outside",
                "Overall: match King Von's flow — confident, measured, not rushed",
            ],
            "cefr_target": "B1→B2",
            "xp_reward": 25,
        },
    },
})

ALL_LESSONS = [
    {
        "id": uuid.UUID("55555555-0001-0001-0001-000000000001"),
        "title": "Lesson 1 — East Coast Block (DD Osama / Kay Flock)",
        "dialect_segment": "east_coast",
        "level_band": "B1",
        "day_order": 1,
        "audio_url": _LESSON_EC_PAYLOAD,
    },
    {
        "id": uuid.UUID("55555555-0002-0002-0002-000000000002"),
        "title": "Lesson 2 — Midwest Block (King Von / Lil Jeff)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 2,
        "audio_url": _LESSON_MW_PAYLOAD,
    },
]

# ── Seed functions ────────────────────────────────────────────────────────────

async def _reset_content(session: AsyncSession) -> None:
    print("  → Borrando lecciones existentes...")
    # Delete old 6-lesson format IDs too
    old_ids = [
        "22222222-0001-0001-0001-000000000001",
        "22222222-0002-0002-0002-000000000002",
        "33333333-0001-0001-0001-000000000001",
        "33333333-0002-0002-0002-000000000002",
        "44444444-0001-0001-0001-000000000001",
        "44444444-0002-0002-0002-000000000002",
    ]
    for lid in old_ids + [str(l["id"]) for l in ALL_LESSONS]:
        await session.execute(text("DELETE FROM lessons WHERE id = :id"), {"id": lid})
    print("  → Borrando vocabulario existente...")
    for vid in [str(v["id"]) for v in VOCABULARY_ITEMS]:
        await session.execute(text("DELETE FROM vocabulary_items WHERE id = :id"), {"id": vid})
    await session.commit()
    print("  ✓ Contenido previo eliminado.")


async def _seed_vocabulary(session: AsyncSession) -> None:
    print(f"  → Insertando {len(VOCABULARY_ITEMS)} términos de vocabulario...")
    for item in VOCABULARY_ITEMS:
        await session.execute(
            text("""
                INSERT INTO vocabulary_items
                    (id, term, definition, example_sentence, dialect_segment, level_band)
                VALUES
                    (:id, :term, :definition, :example_sentence,
                     CAST(:dialect_segment AS dialect_segment_enum),
                     CAST(:level_band AS level_band_enum))
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": str(item["id"]),
                "term": item["term"],
                "definition": item["definition"],
                "example_sentence": item.get("example_sentence"),
                "dialect_segment": item.get("dialect_segment"),
                "level_band": item.get("level_band"),
            },
        )
    await session.commit()
    print(f"  ✓ {len(VOCABULARY_ITEMS)} términos insertados.")


async def _seed_lessons(session: AsyncSession) -> None:
    # Always delete old-format lesson IDs first (they have wrong structure)
    old_ids = [
        "22222222-0001-0001-0001-000000000001",
        "22222222-0002-0002-0002-000000000002",
        "33333333-0001-0001-0001-000000000001",
        "33333333-0002-0002-0002-000000000002",
        "44444444-0001-0001-0001-000000000001",
        "44444444-0002-0002-0002-000000000002",
    ]
    for lid in old_ids:
        await session.execute(text("DELETE FROM lessons WHERE id = :id"), {"id": lid})
    await session.commit()

    print(f"  → Insertando/actualizando {len(ALL_LESSONS)} lecciones...")
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
    print(f"  ✓ {len(ALL_LESSONS)} lecciones insertadas/actualizadas.")


async def _verify(session: AsyncSession) -> None:
    vocab_count = (await session.execute(text("SELECT COUNT(*) FROM vocabulary_items"))).scalar()
    lesson_count = (await session.execute(text("SELECT COUNT(*) FROM lessons"))).scalar()
    print("\n  ┌─────────────────────────────────────────┐")
    print("  │         VERIFICACIÓN POST-SEED          │")
    print("  ├─────────────────────────────────────────┤")
    print(f"  │  vocabulary_items : {vocab_count:<22} │")
    print(f"  │  lessons          : {lesson_count:<22} │")
    print("  └─────────────────────────────────────────┘")


async def main() -> None:
    reset_mode = "--reset" in sys.argv
    print("\n🎤  Drillingo — Database Seeder")
    print("=" * 45)

    async with SessionLocal() as session:
        try:
            await session.execute(text("SELECT 1"))
            print("✓ Conexión a PostgreSQL establecida.\n")
        except Exception as exc:
            print(f"✗ No se pudo conectar: {exc}")
            sys.exit(1)

        if reset_mode:
            print("⚠️  Modo RESET activado...")
            await _reset_content(session)
            print()

        print("📚  Sembrando vocabulario...")
        await _seed_vocabulary(session)

        print("\n🎵  Sembrando lecciones...")
        await _seed_lessons(session)

        print("\n🔍  Verificando...")
        await _verify(session)

    print("\n✅  Seed completado exitosamente.\n")


if __name__ == "__main__":
    asyncio.run(main())
