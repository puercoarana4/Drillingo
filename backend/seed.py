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


# ── VOCABULARY MEGA-DICTIONARY ────────────────────────────────────────────────

VOCABULARY_ITEMS = [
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000001"), "term": "Crash out", "definition": "To lose control and act recklessly, often resulting in losing everything.", "example_sentence": "He crashed out over nothing.", "dialect_segment": None, "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000002"), "term": "Slide", "definition": "To drive to a location, usually enemy territory.", "example_sentence": "We finna slide on them tonight.", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000003"), "term": "Flock", "definition": "To shoot or to rob someone.", "example_sentence": "They tried to flock him for his chain.", "dialect_segment": "east_coast", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000004"), "term": "Tweaking", "definition": "To act irrationally or panic.", "example_sentence": "Bro tweaking, tell him to chill.", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000005"), "term": "Cap", "definition": "To lie. 'No cap' means I am not lying.", "example_sentence": "That's cap, he wasn't there.", "dialect_segment": None, "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000006"), "term": "Snake", "definition": "To betray someone.", "example_sentence": "I thought we was cool but he snaked me.", "dialect_segment": None, "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000007"), "term": "Lurk", "definition": "To wait out of sight or observe secretly.", "example_sentence": "They was lurking block for hours.", "dialect_segment": None, "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000008"), "term": "Drop a dime", "definition": "To inform the police / to snitch.", "example_sentence": "He dropped a dime on the whole crew.", "dialect_segment": "east_coast", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000009"), "term": "Wocky", "definition": "Strange or suspicious.", "example_sentence": "He acting wocky, I don't trust him.", "dialect_segment": "east_coast", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000010"), "term": "Lackin'", "definition": "Caught off guard or unprepared (usually without a weapon).", "example_sentence": "Never get caught lackin at the store.", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000011"), "term": "Fanned out", "definition": "Acting obsessed or starstruck.", "example_sentence": "She was fanned out when she saw him.", "dialect_segment": None, "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000012"), "term": "Valid", "definition": "Acceptable, respected, or good.", "example_sentence": "That spot is valid, the food is crazy.", "dialect_segment": "east_coast", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000013"), "term": "Dayroom", "definition": "Someone who is unreliable or does weird things.", "example_sentence": "He dayroom for leaving his boy like that.", "dialect_segment": "east_coast", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000014"), "term": "On go", "definition": "Ready for action, usually violent.", "example_sentence": "The whole squad is on go right now.", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000015"), "term": "Opp", "definition": "Enemy or opposition.", "example_sentence": "Spotted an opp across the street.", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000016"), "term": "12", "definition": "The police.", "example_sentence": "12 pulling up, everybody scatter.", "dialect_segment": None, "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000017"), "term": "Blick", "definition": "Firearm / Gun.", "example_sentence": "He keep a blick on him at all times.", "dialect_segment": "east_coast", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000018"), "term": "Drop", "definition": "The exact location or address of someone.", "example_sentence": "Send me the drop, I'm on the way.", "dialect_segment": None, "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000019"), "term": "Motion", "definition": "Having momentum, money, or success.", "example_sentence": "He getting real motion this year.", "dialect_segment": None, "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000020"), "term": "Function", "definition": "A party or gathering.", "example_sentence": "We sliding to the function later.", "dialect_segment": "east_coast", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000021"), "term": "Merch it", "definition": "Swear on it / Promise me.", "example_sentence": "Merch it you saw him there.", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000022"), "term": "Expeditiously", "definition": "Immediately and quickly.", "example_sentence": "Get over here expeditiously.", "dialect_segment": "east_coast", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000023"), "term": "Word to my dead", "definition": "I swear on my deceased relatives.", "example_sentence": "Word to my dead I ain't do that.", "dialect_segment": "east_coast", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000024"), "term": "Finna", "definition": "Contracted 'fixing to' — immediate future intent. AAVE equivalent of 'going to'.", "example_sentence": "We finna slide — We are about to go confront them.", "dialect_segment": None, "level_band": "B1"},
]


# ── PHASE 1 LESSONS: 4 Lessons Representing Weeks 1 to 4 ──────────────────────

_L1_ZERO_COPULA = _jdump({
    "lesson_title": "W1: Zero Copula (Absence of 'To Be')",
    "dialect_focus": "Midwest / Chicago",
    "modules": {
        "reading": {
            "module_type": "reading",
            "dialect_focus": "Chicago Drill",
            "raw_text": "yo he tweaking, tell him we outside",
            "formal_translation": "Hey, he is acting irrationally. Tell him that we are outside.",
            "breakdown": [
                {"abbr": "tweaking", "meaning": "acting crazy or paranoid"},
                {"abbr": "we outside", "meaning": "we are outside / actively in the streets"},
            ],
            "grammar_notes": [
                "Zero Copula: AAVE often omits the verb 'to be' (is/are) when it acts as a linking verb in present tense.",
                "Instead of 'he is tweaking', it is just 'he tweaking'.",
                "Instead of 'we are outside', it is 'we outside'."
            ],
            "cefr_target": "B1",
            "xp_reward": 10,
        },
        "listening": {
            "module_type": "listening",
            "artist": "Chief Keef / Midwest",
            "dialect_focus": "Midwest / Chicago",
            "audio_s3_url": "dummy",
            "youtube_video_id": "g0v7Ow6Epog",  # Reusing Von video for testing
            "original_bar": "We finna slide, merch it on Von you ain't outside.",
            "exercise_text": "We ______ slide, ______ it on Von you ain't outside.",
            "blanks": [
                {"position": 1, "correct_answers": ["finna"], "hint": "About to / going to", "distractor_options": ["gonna", "bout"]},
                {"position": 2, "correct_answers": ["merch", "Merch"], "hint": "Swear on it", "distractor_options": ["swear", "put"]},
            ],
            "full_translation": "We are about to drive over there. Swear on King Von that you are not outside.",
            "grammar_notes": ["'You ain't outside' acts as a negated copula. 'Outside' means active in the streets."],
            "cefr_target": "B1",
            "xp_reward": 15,
        },
        "writing": {
            "module_type": "writing",
            "formal_input": "He is acting crazy. They are outside.",
            "expected_drill_output": "He tweaking, they outside",
            "accepted_variants": ["He tweaking, they outside", "He tweaking they outside", "He buggin, they outside"],
            "evaluation_rubric": {
                "zero_copula_1": {"description": "Drops 'is' before acting crazy", "points": 50, "example": "'He tweaking' ✓"},
                "zero_copula_2": {"description": "Drops 'are' before outside", "points": 50, "example": "'They outside' ✓"},
            },
            "grammar_explanation": "Drop 'is' and 'are'. Use 'tweaking' or 'buggin' for acting crazy.",
            "cefr_target": "B1",
            "xp_reward": 20,
        },
        "speaking": {
            "module_type": "speaking",
            "target_phrase": "He tweaking, tell him we outside.",
            "phonetic_tips": ["Blend 'we' and 'outside' smoothly.", "Drop the 'g' in tweaking."],
            "cefr_target": "B1",
            "xp_reward": 25,
        },
    },
})

_L2_NEGATIVE_CONCORD = _jdump({
    "lesson_title": "W2: Negative Concord (Double Negation)",
    "dialect_focus": "East Coast / NYC",
    "modules": {
        "reading": {
            "module_type": "reading",
            "dialect_focus": "East Coast Drill",
            "raw_text": "wrd2my-mom I ain't got no money, ain't nobody doing nothing",
            "formal_translation": "I swear on my mother I do not have any money, nobody is doing anything.",
            "breakdown": [
                {"abbr": "wrd2my-mom", "meaning": "word to my mother (I swear)"},
                {"abbr": "ain't got no", "meaning": "do not have any"},
            ],
            "grammar_notes": [
                "Negative Concord: Multiple negative words are used to emphasize the negation, not cancel it.",
                "'ain't got no money' = do not have any money.",
                "'ain't nobody doing nothing' = triple negation for emphasis."
            ],
            "cefr_target": "B1+",
            "xp_reward": 10,
        },
        "listening": {
            "module_type": "listening",
            "artist": "Kay Flock",
            "dialect_focus": "East Coast / NYC",
            "audio_s3_url": "dummy",
            "youtube_video_id": "gGJS8W9emac",
            "original_bar": "Word to my mom, I ain't runnin' from no opp.",
            "exercise_text": "______ to my mom, I ______ runnin' from no opp.",
            "blanks": [
                {"position": 1, "correct_answers": ["Word", "word"], "hint": "Oath", "distractor_options": ["Swear", "True"]},
                {"position": 2, "correct_answers": ["ain't", "aint"], "hint": "Am not", "distractor_options": ["don't", "won't"]},
            ],
            "full_translation": "I swear on my mother, I am not running from any enemy.",
            "grammar_notes": ["'ain't runnin from no opp' is double negation for emphasis."],
            "cefr_target": "B1+",
            "xp_reward": 15,
        },
        "writing": {
            "module_type": "writing",
            "formal_input": "I do not have any money. Nobody is doing anything.",
            "expected_drill_output": "I ain't got no money, ain't nobody doing nothing",
            "accepted_variants": ["I ain't got no money, ain't nobody doing nothing", "I ain't got no bread, ain't nobody doing nothing"],
            "evaluation_rubric": {
                "double_negation": {"description": "Uses 'ain't got no'", "points": 50, "example": "'ain't got no money' ✓"},
                "triple_negation": {"description": "Uses 'ain't nobody doing nothing'", "points": 50, "example": "'ain't nobody doing nothing' ✓"},
            },
            "grammar_explanation": "Stack negatives to increase emphasis. Replace 'any' with 'no' and 'anything' with 'nothing'.",
            "cefr_target": "B1+",
            "xp_reward": 20,
        },
        "speaking": {
            "module_type": "speaking",
            "target_phrase": "I ain't got no money, ain't nobody doing nothing.",
            "phonetic_tips": ["Say 'ain't' sharply.", "Link 'got no' smoothly."],
            "cefr_target": "B1+",
            "xp_reward": 25,
        },
    },
})

_L3_INVERTED_SYNTAX = _jdump({
    "lesson_title": "W3: Inverted Syntax (Questions without Auxiliaries)",
    "dialect_focus": "Chicago / NYC",
    "modules": {
        "reading": {
            "module_type": "reading",
            "dialect_focus": "General Drill",
            "raw_text": "where you going bro? why he do that?",
            "formal_translation": "Where are you going brother? Why did he do that?",
            "breakdown": [
                {"abbr": "where you going", "meaning": "Where are you going"},
                {"abbr": "why he do that", "meaning": "Why did he do that"},
            ],
            "grammar_notes": [
                "Inverted Syntax: Auxiliary verbs like 'do', 'does', 'did', and 'are' are completely dropped in questions.",
                "The word order remains the same as a statement, but with question intonation."
            ],
            "cefr_target": "B1+",
            "xp_reward": 10,
        },
        "listening": {
            "module_type": "listening",
            "artist": "General Drill",
            "dialect_focus": "General",
            "audio_s3_url": "dummy",
            "youtube_video_id": "g0v7Ow6Epog", # Dummy reuse
            "original_bar": "Where you going with that blick?",
            "exercise_text": "______ you going with that ______?",
            "blanks": [
                {"position": 1, "correct_answers": ["Where", "where"], "hint": "Question word", "distractor_options": ["Why", "How"]},
                {"position": 2, "correct_answers": ["blick"], "hint": "Firearm", "distractor_options": ["pole", "stick"]},
            ],
            "full_translation": "Where are you going with that gun?",
            "grammar_notes": ["'Where you going' omits the auxiliary 'are'."],
            "cefr_target": "B1+",
            "xp_reward": 15,
        },
        "writing": {
            "module_type": "writing",
            "formal_input": "Where are you going? Why did he do that?",
            "expected_drill_output": "Where you going? Why he do that?",
            "accepted_variants": ["Where you going? Why he do that", "Where you going bro? Why he do that"],
            "evaluation_rubric": {
                "drop_aux_1": {"description": "Drops 'are' in the first question", "points": 50, "example": "'Where you going?' ✓"},
                "drop_aux_2": {"description": "Drops 'did' in the second question", "points": 50, "example": "'Why he do that?' ✓"},
            },
            "grammar_explanation": "Remove the helper verbs (are, did) completely to form the question natively.",
            "cefr_target": "B1+",
            "xp_reward": 20,
        },
        "speaking": {
            "module_type": "speaking",
            "target_phrase": "Where you going? Why he do that?",
            "phonetic_tips": ["Rise your pitch at the end to indicate a question."],
            "cefr_target": "B1+",
            "xp_reward": 25,
        },
    },
})

_L4_PAST_PARTICIPLE = _jdump({
    "lesson_title": "W4: Simple Past vs Participle",
    "dialect_focus": "Midwest",
    "modules": {
        "reading": {
            "module_type": "reading",
            "dialect_focus": "Chicago Drill",
            "raw_text": "he gone there yesterday, I seen it with my own eyes",
            "formal_translation": "He went there yesterday, I saw it with my own eyes.",
            "breakdown": [
                {"abbr": "he gone", "meaning": "he went"},
                {"abbr": "I seen", "meaning": "I saw"},
            ],
            "grammar_notes": [
                "Participle for Past: AAVE frequently swaps the simple past form with the past participle.",
                "'went' becomes 'gone'.",
                "'saw' becomes 'seen'."
            ],
            "cefr_target": "B2",
            "xp_reward": 10,
        },
        "listening": {
            "module_type": "listening",
            "artist": "General Drill",
            "dialect_focus": "Midwest",
            "audio_s3_url": "dummy",
            "youtube_video_id": "gGJS8W9emac", # Dummy reuse
            "original_bar": "I seen him lacking on the block.",
            "exercise_text": "I ______ him ______ on the block.",
            "blanks": [
                {"position": 1, "correct_answers": ["seen"], "hint": "Saw", "distractor_options": ["saw", "see"]},
                {"position": 2, "correct_answers": ["lacking", "lackin"], "hint": "Caught off guard", "distractor_options": ["slippin", "hiding"]},
            ],
            "full_translation": "I saw him unprepared on the street.",
            "grammar_notes": ["'I seen' replaces 'I saw'."],
            "cefr_target": "B2",
            "xp_reward": 15,
        },
        "writing": {
            "module_type": "writing",
            "formal_input": "He went there. I saw it.",
            "expected_drill_output": "He gone there, I seen it",
            "accepted_variants": ["He gone there, I seen it", "He gone there I seen it"],
            "evaluation_rubric": {
                "gone_usage": {"description": "Replaces 'went' with 'gone'", "points": 50, "example": "'He gone' ✓"},
                "seen_usage": {"description": "Replaces 'saw' with 'seen'", "points": 50, "example": "'I seen it' ✓"},
            },
            "grammar_explanation": "Use the past participle form (gone, seen) without 'have' for simple past actions.",
            "cefr_target": "B2",
            "xp_reward": 20,
        },
        "speaking": {
            "module_type": "speaking",
            "target_phrase": "He gone there, I seen it.",
            "phonetic_tips": ["Elongate the 'o' in gone slightly.", "Emphasis on 'seen'."],
            "cefr_target": "B2",
            "xp_reward": 25,
        },
    },
})


ALL_LESSONS = [
    {
        "id": uuid.UUID("55555555-0001-0001-0001-000000000001"),
        "title": "Week 1: Zero Copula (Absence of 'To Be')",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 1,
        "audio_url": _L1_ZERO_COPULA,
    },
    {
        "id": uuid.UUID("55555555-0002-0002-0002-000000000002"),
        "title": "Week 2: Negative Concord (Double Negation)",
        "dialect_segment": "east_coast",
        "level_band": "B1",
        "day_order": 2,
        "audio_url": _L2_NEGATIVE_CONCORD,
    },
    {
        "id": uuid.UUID("55555555-0003-0003-0003-000000000003"),
        "title": "Week 3: Inverted Syntax (Questions)",
        "dialect_segment": "east_coast",
        "level_band": "B1",
        "day_order": 3,
        "audio_url": _L3_INVERTED_SYNTAX,
    },
    {
        "id": uuid.UUID("55555555-0004-0004-0004-000000000004"),
        "title": "Week 4: Simple Past vs Participle",
        "dialect_segment": "midwest",
        "level_band": "B2",
        "day_order": 4,
        "audio_url": _L4_PAST_PARTICIPLE,
    },
]


# ── Seed functions ────────────────────────────────────────────────────────────

async def _reset_content(session: AsyncSession) -> None:
    print("  → Borrando lecciones existentes...")
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
    old_ids = [
        "22222222-0001-0001-0001-000000000001",
        "22222222-0002-0002-0002-000000000002",
        "33333333-0001-0001-0001-000000000001",
        "33333333-0002-0002-0002-000000000002",
        "44444444-0001-0001-0001-000000000001",
        "44444444-0002-0002-0002-000000000002",
        "55555555-0001-0001-0001-000000000001",
        "55555555-0002-0002-0002-000000000002",
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
