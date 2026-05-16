"""
seed.py — Drillingo Database Seeder
====================================
Pobla todas las tablas con contenido pedagógico real para llevar al usuario
de B1 a C1 usando AAVE / Drill americano como vehículo de aprendizaje.

Uso:
    cd backend
    python seed.py                  # inserta datos (skip si ya existen)
    python seed.py --reset          # borra todo y re-inserta

Nota sobre la tabla `lessons`:
    El esquema actual no tiene columna JSONB para contenido de ejercicios.
    El payload estructurado (blanks, answers, translations, breakdowns) se
    serializa como JSON y se almacena en `audio_url` para lecciones de tipo
    reading/writing.  Las lecciones de listening usan la URL real de S3.
    Esto es intencional hasta que se agregue una columna `content_json JSONB`.
"""

import asyncio
import json
import os
import sys
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# ---------------------------------------------------------------------------
# Engine setup — lee DATABASE_URL del entorno (Railway lo inyecta)
# ---------------------------------------------------------------------------

def _build_async_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        # Fallback: intentar cargar desde .env en el mismo directorio
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DATABASE_URL="):
                        url = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not url:
        raise RuntimeError(
            "DATABASE_URL no está definida. "
            "Exporta la variable o asegúrate de que .env existe."
        )
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


engine = create_async_engine(_build_async_url(), echo=False, future=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uid() -> uuid.UUID:
    """Genera un UUID v4 determinístico-ish para reproducibilidad."""
    return uuid.uuid4()


def _jdump(obj: dict) -> str:
    """Serializa un dict a JSON compacto para almacenar en audio_url."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# 1. VOCABULARY — 6 términos clave B1→C1
# ---------------------------------------------------------------------------

VOCABULARY_ITEMS = [
    {
        "id": uuid.UUID("11111111-0001-0001-0001-000000000001"),
        "term": "Buggin'",
        "definition": (
            "Acting erratically, irrationally, or in a way that makes no sense. "
            "Derived from 'bugging out'. Core East Coast AAVE. "
            "Grammatically functions as a present-participle predicate adjective "
            "after a dropped copula: 'He buggin'' = 'He is bugging out'."
        ),
        "example_sentence": (
            "Drill context: 'Wrd2my-mom he buggin smh' — "
            "Translation: 'I swear on my mother he is acting irrational, shaking my head.' "
            "Formal B2 equivalent: 'He is behaving irrationally and I cannot believe it.'"
        ),
        "dialect_segment": "east_coast",
        "level_band": "B1",
    },
    {
        "id": uuid.UUID("11111111-0002-0002-0002-000000000002"),
        "term": "Merch it",
        "definition": (
            "To kill someone; to 'put them on a shirt' (merchandise), "
            "referencing memorial t-shirts printed for the deceased. "
            "Midwest / Chicago drill slang. Verb phrase, transitive. "
            "C1 register: euphemistic nominalization of lethal violence."
        ),
        "example_sentence": (
            "Drill context: 'Merch it on Von you ain't outside' — "
            "Translation: 'I swear on Von [King Von] you are not in the streets.' "
            "Formal C1 equivalent: 'I stake my reputation on the fact that you are not present in that environment.'"
        ),
        "dialect_segment": "midwest",
        "level_band": "C1",
    },
    {
        "id": uuid.UUID("11111111-0003-0003-0003-000000000003"),
        "term": "Finna",
        "definition": (
            "Contracted form of 'fixing to' — expresses immediate future intent. "
            "AAVE grammatical marker equivalent to 'going to' / 'about to'. "
            "Key grammar point: 'finna' replaces 'going to' entirely and never "
            "co-occurs with 'be' in AAVE: 'I finna go' NOT 'I am finna go'."
        ),
        "example_sentence": (
            "Drill context: 'We finna slide' — "
            "Translation: 'We are about to go [to confront someone].' "
            "Formal B1 equivalent: 'We are going to leave immediately.' "
            "Grammar drill: Replace 'going to' with 'finna' and drop the auxiliary 'be'."
        ),
        "dialect_segment": None,  # General AAVE — no region restriction
        "level_band": "B1",
    },
    {
        "id": uuid.UUID("11111111-0004-0004-0004-000000000004"),
        "term": "Opp",
        "definition": (
            "Short for 'opponent' or 'opposition'. Refers to a rival, enemy, "
            "or anyone perceived as a threat. General AAVE / drill slang. "
            "Plural 'opps' is more common. "
            "C1 nuance: carries connotation of active, known adversary — "
            "stronger than 'enemy', implies ongoing conflict."
        ),
        "example_sentence": (
            "Drill context: 'I ain't runnin from no opp' — "
            "Translation: 'I am not running away from any opponent.' "
            "Grammar note: double negation ('ain't' + 'no') is grammatically "
            "correct in AAVE and intensifies the negation rather than canceling it."
        ),
        "dialect_segment": "east_coast",
        "level_band": "B2",
    },
    {
        "id": uuid.UUID("11111111-0005-0005-0005-000000000005"),
        "term": "Deadass",
        "definition": (
            "Adverb/adjective meaning 'seriously', 'for real', 'without any doubt'. "
            "East Coast AAVE, heavily associated with NYC. "
            "Functions as a sentence-initial intensifier or predicate adjective. "
            "Equivalent to 'literally' in standard informal English but stronger."
        ),
        "example_sentence": (
            "Drill context: 'Deadass he don't know nobody on this block' — "
            "Translation: 'Seriously, he does not know anyone on this block.' "
            "Formal B2 equivalent: 'I am completely serious — he is not acquainted with anyone in this area.' "
            "Note: 'don't know nobody' = AAVE double negation = emphatic 'does not know anyone'."
        ),
        "dialect_segment": "east_coast",
        "level_band": "B2",
    },
    {
        "id": uuid.UUID("11111111-0006-0006-0006-000000000006"),
        "term": "Backdoor",
        "definition": (
            "To betray someone from within; to set someone up while pretending "
            "to be their ally. Chicago/Midwest drill slang. Verb, transitive. "
            "C1 register: implies premeditated deception by a trusted associate — "
            "semantically closer to 'betray' than 'ambush'."
        ),
        "example_sentence": (
            "Drill context: 'They backdoored him, he thought they was solid' — "
            "Translation: 'They betrayed him; he believed they were trustworthy.' "
            "Formal C1 equivalent: 'He was deceived by individuals he considered loyal allies.' "
            "Grammar note: 'was solid' — AAVE uses 'was' for all persons in past tense."
        ),
        "dialect_segment": "midwest",
        "level_band": "C1",
    },
]

# ---------------------------------------------------------------------------
# 2. LESSONS — Reading: "Street Texts" (DMs de Instagram)
# ---------------------------------------------------------------------------
# El payload del ejercicio se serializa en `audio_url` como JSON porque la
# tabla `lessons` no tiene columna JSONB dedicada.  El cliente debe detectar
# si audio_url empieza con '{' para tratarlo como contenido de ejercicio.

_READING_EC_PAYLOAD = _jdump({
    "module_type": "reading",
    "exercise_type": "street_text_decode",
    "dialect_focus": "East Coast — DD Osama / Kay Flock",
    "raw_text": "yo wtw? idn what he talkin bout fr, wrd2my-mom he buggin smh",
    "formal_translation": (
        "Hey, what's going on? I don't know what he is talking about, "
        "for real. I swear on my mother he is acting irrational, "
        "shaking my head."
    ),
    "breakdown": [
        {"abbr": "yo",         "meaning": "Hey / informal greeting (vocative)"},
        {"abbr": "wtw",        "meaning": "What's the word? / What's going on? (East Coast)"},
        {"abbr": "idn",        "meaning": "I don't know"},
        {"abbr": "talkin bout","meaning": "talking about (dropped -g, AAVE)"},
        {"abbr": "fr",         "meaning": "for real — intensifier, confirms sincerity"},
        {"abbr": "wrd2my-mom", "meaning": "word to my mother — oath of truth (East Coast)"},
        {"abbr": "buggin",     "meaning": "acting irrationally (see vocabulary: Buggin')"},
        {"abbr": "smh",        "meaning": "shaking my head — expresses disappointment/disbelief"},
    ],
    "grammar_notes": [
        "Dropped copula: 'he buggin' = 'he is bugging' — AAVE omits 'is' in present progressive.",
        "'talkin bout' — progressive -ing reduced to -in' in casual AAVE speech.",
        "No punctuation except '?' — mirrors real DM/text register.",
    ],
    "cefr_target": "B1→B2",
    "xp_reward": 30,
})

_READING_MW_PAYLOAD = _jdump({
    "module_type": "reading",
    "exercise_type": "street_text_decode",
    "dialect_focus": "Midwest / Chicago — Lil Jeff / Bloodhound Q50",
    "raw_text": "wfs? slide to the block, we tryna see wtw, don't dodge",
    "formal_translation": (
        "What's up? Come to the neighborhood, we are trying to find out "
        "what is going on. Do not avoid us."
    ),
    "breakdown": [
        {"abbr": "wfs",    "meaning": "What's the fuck's up? / What's going on? (Chicago)"},
        {"abbr": "slide",  "meaning": "to come through / travel to a location (Midwest drill)"},
        {"abbr": "block",  "meaning": "the neighborhood block where the crew hangs"},
        {"abbr": "tryna",  "meaning": "trying to (contracted, AAVE)"},
        {"abbr": "wtw",    "meaning": "what's the word / what's happening"},
        {"abbr": "dodge",  "meaning": "to avoid, evade, or not show up (Chicago slang)"},
    ],
    "grammar_notes": [
        "'tryna' = 'trying to' — AAVE contraction, functions as modal-like future intent.",
        "Imperative 'slide' — no subject, direct command register.",
        "'don't dodge' — standard negation but in drill context carries threat implication.",
        "Chicago drill texts often omit punctuation and use minimal capitalization.",
    ],
    "cefr_target": "B1→B2",
    "xp_reward": 30,
})

READING_LESSONS = [
    {
        "id": uuid.UUID("22222222-0001-0001-0001-000000000001"),
        "title": "Street Texts #1 — East Coast DM (DD Osama / Kay Flock)",
        "dialect_segment": "east_coast",
        "level_band": "B1",
        "day_order": 1,
        "audio_url": _READING_EC_PAYLOAD,
    },
    {
        "id": uuid.UUID("22222222-0002-0002-0002-000000000002"),
        "title": "Street Texts #2 — Chicago DM (Lil Jeff / Bloodhound Q50)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 2,
        "audio_url": _READING_MW_PAYLOAD,
    },
]

# ---------------------------------------------------------------------------
# 3. LESSONS — Listening: "The Cypher" (fill-in-the-blanks)
# ---------------------------------------------------------------------------

_LISTENING_MW_PAYLOAD = _jdump({
    "module_type": "listening",
    "exercise_type": "fill_in_the_blanks",
    "artist": "King Von",
    "dialect_focus": "Midwest / Chicago",
    "audio_s3_url": "https://drillingo-assets.s3.amazonaws.com/audio/king_von_finna_slide.mp3",
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
        "We are about to go [confront them]. I swear on King Von "
        "you are not actually in the streets."
    ),
    "grammar_notes": [
        "'finna slide' — 'finna' replaces 'going to'; 'slide' = travel to confront.",
        "'merch it on Von' — oath using a deceased artist's name as a truth marker.",
        "'you ain't outside' — 'ain't' = 'are not'; 'outside' = active in the streets.",
    ],
    "cefr_target": "B2→C1",
    "xp_reward": 50,
})

_LISTENING_EC_PAYLOAD = _jdump({
    "module_type": "listening",
    "exercise_type": "fill_in_the_blanks",
    "artist": "Kay Flock",
    "dialect_focus": "East Coast / NYC",
    "audio_s3_url": "https://drillingo-assets.s3.amazonaws.com/audio/kay_flock_word_to_my_mom.mp3",
    "original_bar": "Word to my mom, I ain't runnin' from no opp.",
    "exercise_text": "______ to my mom, I ______ runnin' from no opp.",
    "blanks": [
        {
            "position": 1,
            "correct_answers": ["Word", "word"],
            "hint": "East Coast oath / truth affirmation (see vocabulary: wrd2my-mom)",
            "distractor_options": ["Word", "Swear", "True", "Real"],
        },
        {
            "position": 2,
            "correct_answers": ["ain't", "aint"],
            "hint": "AAVE negation of 'am not' / 'is not' / 'are not'",
            "distractor_options": ["ain't", "won't", "don't", "can't"],
        },
    ],
    "full_translation": (
        "I swear on my mother, I am not running away from any opponent."
    ),
    "grammar_notes": [
        "'Word to my mom' — East Coast oath, equivalent to 'I swear on my mother'.",
        "'ain't runnin'' — AAVE: 'ain't' + present participle = emphatic present progressive negation.",
        "'from no opp' — double negation: 'ain't' + 'no' = emphatic 'not from any opponent'.",
        "Double negation in AAVE is grammatically correct and intensifies, not cancels.",
    ],
    "cefr_target": "B2→C1",
    "xp_reward": 50,
})

LISTENING_LESSONS = [
    {
        "id": uuid.UUID("33333333-0001-0001-0001-000000000001"),
        "title": "The Cypher #1 — King Von: 'Finna Slide' (Midwest)",
        "dialect_segment": "midwest",
        "level_band": "B2",
        "day_order": 3,
        "audio_url": _LISTENING_MW_PAYLOAD,
    },
    {
        "id": uuid.UUID("33333333-0002-0002-0002-000000000002"),
        "title": "The Cypher #2 — Kay Flock: 'Word to My Mom' (East Coast)",
        "dialect_segment": "east_coast",
        "level_band": "B2",
        "day_order": 4,
        "audio_url": _LISTENING_EC_PAYLOAD,
    },
]

# ---------------------------------------------------------------------------
# 4. LESSONS — Writing: "Spitting Bars" (traducción inversa formal→drill)
# ---------------------------------------------------------------------------

_WRITING_01_PAYLOAD = _jdump({
    "module_type": "writing",
    "exercise_type": "inverse_translation",
    "challenge_id": "writing_01",
    "formal_input": "I do not have any money and I am not going to do that.",
    "formal_level": "B1/B2 Standard English",
    "expected_drill_output": "I ain't got no money and I ain't finna do allat",
    "accepted_variants": [
        "I ain't got no money and I ain't finna do allat",
        "I ain't got no money and I ain't finna do all that",
        "Ain't got no money and ain't finna do allat",
        "I ain't got no bread and I ain't finna do allat",
    ],
    "evaluation_rubric": {
        "double_negation": {
            "description": "Uses 'ain't' + 'no' for emphatic negation (not 'don't have any')",
            "points": 30,
            "example": "'ain't got no money' ✓ — 'don't have any money' ✗",
        },
        "dropped_copula": {
            "description": "Omits 'am' before 'not going to' — uses 'ain't finna' directly",
            "points": 30,
            "example": "'ain't finna do' ✓ — 'am not going to do' ✗",
        },
        "finna_usage": {
            "description": "Replaces 'going to' with 'finna' as future marker",
            "points": 20,
            "example": "'finna do' ✓ — 'gonna do' partial credit",
        },
        "allat_compression": {
            "description": "Compresses 'all of that' / 'that' to 'allat' (optional, C1 bonus)",
            "points": 20,
            "example": "'allat' ✓ — 'all that' partial credit",
        },
    },
    "grammar_explanation": (
        "AAVE double negation: 'ain't got no' is grammatically correct and emphatic. "
        "Standard English 'I do not have any' maps to AAVE 'I ain't got no'. "
        "'Finna' replaces 'going to' entirely — never say 'am finna'. "
        "'Allat' is a phonological compression of 'all of that' common in drill lyrics."
    ),
    "cefr_target": "B2→C1",
    "xp_reward": 60,
})

_WRITING_02_PAYLOAD = _jdump({
    "module_type": "writing",
    "exercise_type": "inverse_translation",
    "challenge_id": "writing_02",
    "formal_input": "He is acting crazy, he does not know anyone here.",
    "formal_level": "B1/B2 Standard English",
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
        "In AAVE, the copula 'is' is regularly omitted in present progressive. "
        "Double negation: 'don't know nobody' = emphatic 'does not know anyone'. "
        "Note: 'don't' is used for all persons in AAVE present tense "
        "('he don't', 'she don't') — no third-person -s."
    ),
    "cefr_target": "B2→C1",
    "xp_reward": 60,
})

WRITING_LESSONS = [
    {
        "id": uuid.UUID("44444444-0001-0001-0001-000000000001"),
        "title": "Spitting Bars #1 — Double Negation & Finna (B1→Drill)",
        "dialect_segment": "east_coast",
        "level_band": "B2",
        "day_order": 5,
        "audio_url": _WRITING_01_PAYLOAD,
    },
    {
        "id": uuid.UUID("44444444-0002-0002-0002-000000000002"),
        "title": "Spitting Bars #2 — Dropped Copula & Don't Know Nobody (B1→Drill)",
        "dialect_segment": "midwest",
        "level_band": "B2",
        "day_order": 6,
        "audio_url": _WRITING_02_PAYLOAD,
    },
]

ALL_LESSONS = READING_LESSONS + LISTENING_LESSONS + WRITING_LESSONS

# ---------------------------------------------------------------------------
# Core seed functions
# ---------------------------------------------------------------------------

async def _reset_content(session: AsyncSession) -> None:
    """
    Borra los registros semilla en orden seguro (respeta FK constraints).
    NO borra usuarios ni su progreso — solo el contenido semilla con IDs conocidos.
    """
    print("  → Borrando lecciones existentes...")
    lesson_ids = [str(l["id"]) for l in ALL_LESSONS]
    for lid in lesson_ids:
        await session.execute(
            text("DELETE FROM lessons WHERE id = :id"),
            {"id": lid},
        )
    print("  → Borrando vocabulario existente...")
    vocab_ids = [str(v["id"]) for v in VOCABULARY_ITEMS]
    for vid in vocab_ids:
        await session.execute(
            text("DELETE FROM vocabulary_items WHERE id = :id"),
            {"id": vid},
        )
    await session.commit()
    print("  ✓ Contenido previo eliminado.")


async def _seed_vocabulary(session: AsyncSession) -> None:
    """Inserta vocabulary_items. Usa ON CONFLICT DO NOTHING para idempotencia."""
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
    """Inserta todas las lecciones. Usa ON CONFLICT DO NOTHING para idempotencia."""
    print(f"  → Insertando {len(ALL_LESSONS)} lecciones...")
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
                ON CONFLICT (id) DO NOTHING
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
    print(f"  ✓ {len(ALL_LESSONS)} lecciones insertadas.")

async def _verify(session: AsyncSession) -> None:
    """Imprime un resumen de lo que quedó en la base de datos."""
    vocab_count = (await session.execute(text("SELECT COUNT(*) FROM vocabulary_items"))).scalar()
    lesson_count = (await session.execute(text("SELECT COUNT(*) FROM lessons"))).scalar()
    ec_lessons = (await session.execute(
        text("SELECT COUNT(*) FROM lessons WHERE dialect_segment = 'east_coast'")
    )).scalar()
    mw_lessons = (await session.execute(
        text("SELECT COUNT(*) FROM lessons WHERE dialect_segment = 'midwest'")
    )).scalar()

    print("\n  ┌─────────────────────────────────────────┐")
    print("  │         VERIFICACIÓN POST-SEED          │")
    print("  ├─────────────────────────────────────────┤")
    print(f"  │  vocabulary_items total : {vocab_count:<14} │")
    print(f"  │  lessons total          : {lesson_count:<14} │")
    print(f"  │    └─ east_coast        : {ec_lessons:<14} │")
    print(f"  │    └─ midwest           : {mw_lessons:<14} │")
    print("  └─────────────────────────────────────────┘")


# ---------------------------------------------------------------------------
# Entrypoint principal
# ---------------------------------------------------------------------------

async def main() -> None:
    reset_mode = "--reset" in sys.argv

    print("\n🎤  Drillingo — Database Seeder")
    print("=" * 45)

    if reset_mode:
        print("⚠️  Modo RESET activado — borrando datos semilla previos...")

    async with SessionLocal() as session:
        # Verificar conexión
        try:
            await session.execute(text("SELECT 1"))
            print("✓ Conexión a PostgreSQL establecida.\n")
        except Exception as exc:
            print(f"✗ No se pudo conectar a la base de datos: {exc}")
            sys.exit(1)

        if reset_mode:
            await _reset_content(session)
            print()

        print("📚  Sembrando vocabulario...")
        await _seed_vocabulary(session)

        print("\n🎵  Sembrando lecciones...")
        await _seed_lessons(session)

        print("\n🔍  Verificando...")
        await _verify(session)

    print("\n✅  Seed completado exitosamente.")
    print("    Drillingo está listo para llevar usuarios de B1 a C1.\n")


if __name__ == "__main__":
    asyncio.run(main())
