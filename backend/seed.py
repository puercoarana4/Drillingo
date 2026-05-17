"""
seed.py — Drillingo Database Seeder
====================================
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

VOCABULARY_ITEMS = [
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000001"), "term": "Crash out", "definition": "Perder el control y actuar de forma imprudente.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000002"), "term": "Slide", "definition": "Conducir a un lugar para confrontar a alguien (atacar).", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000003"), "term": "Flock", "definition": "Disparar o robar a alguien.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000004"), "term": "Tweaking", "definition": "Actuar irracionalmente o entrar en pánico (estar loco).", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000005"), "term": "Cap", "definition": "Mentir. 'No cap' significa no estoy mintiendo.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000006"), "term": "Snake", "definition": "Traicionar a alguien.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000007"), "term": "Lurk", "definition": "Esperar fuera de la vista (acechar).", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000008"), "term": "Drop a dime", "definition": "Informar a la policía (delatar).", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000009"), "term": "Wocky", "definition": "Extraño o sospechoso.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000010"), "term": "Lackin'", "definition": "Atrapado sin preparación (con la guardia baja).", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000011"), "term": "Fanned out", "definition": "Actuar obsesionado (como un fan).", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000012"), "term": "Valid", "definition": "Aceptable o bueno.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000013"), "term": "Dayroom", "definition": "Alguien que no es confiable o es aburrido.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000014"), "term": "On go", "definition": "Listo para la acción en cualquier momento.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000015"), "term": "Opp", "definition": "Enemigo u oposición.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000016"), "term": "12", "definition": "La policía.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000017"), "term": "Blick", "definition": "Arma de fuego / Pistola.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000018"), "term": "Drop", "definition": "Ubicación / Dirección exacta.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000019"), "term": "Motion", "definition": "Tener impulso, éxito o dinero.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000020"), "term": "Function", "definition": "Una fiesta o reunión.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000021"), "term": "Merch it", "definition": "Júralo (por algo/alguien).", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000022"), "term": "Expeditiously", "definition": "Inmediatamente y muy rápido.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000023"), "term": "Word to my dead", "definition": "Lo juro por mis familiares fallecidos.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000024"), "term": "Finna", "definition": "A punto de / voy a (going to).", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
]

ALL_LESSONS = [
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000001"),
        "title": "D1: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 1,
        "audio_url": _jdump({"lesson_title": "D1: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking right now. They outside the block waiting. You lackin' if you don't stay alert. We finna slide.", "formal_translation": "Formal: He is acting irrationally right now. They are outside... | Español: Él está actuando irracionalmente ahora. Ellos están afuera del bloque esperando. Estás desprevenido si no te mantienes alerta. Estamos a punto de ir.", "breakdown": [{"abbr": "tweaking", "meaning": "actuando irracionalmente (loco)"}, {"abbr": "they outside", "meaning": "ellos están afuera"}, {"abbr": "lackin'", "meaning": "desprevenido (con la guardia baja)"}, {"abbr": "finna slide", "meaning": "a punto de ir (atacar)"}], "grammar_notes": ["Zero Copula: Se omite el verbo 'to be' (ser/estar). Ej: 'He is tweaking' se convierte en 'He tweaking'."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end. We outside. He tweaking.", "exercise_text": "These girls ______ Sosa, O end or ______ end. We ______. He ______.", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "amar/adorar", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negativo", "distractor_options": ["know", "go"]}, {"position": 3, "correct_answers": ["outside"], "hint": "afuera", "distractor_options": ["inside", "away"]}, {"position": 4, "correct_answers": ["tweaking"], "hint": "actuando loco", "distractor_options": ["chilling", "sleeping"]}], "full_translation": "A estas chicas les encanta Sosa, es O block o nada. Estamos afuera. Él está actuando loco.", "grammar_notes": ["Contexto de Zero Copula en el drill típico de Chicago. (We [are] outside)."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside. You are unprepared.", "expected_drill_output": "He tweaking. They outside. You lackin.", "accepted_variants": ["He tweaking, they outside, you lackin", "He buggin, they outside, you lackin"], "evaluation_rubric": {"zero_copula": {"description": "Omite 'is' y 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Elimina 'is' y 'are' para formar la Zero Copula (omisión del verbo to be).", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside right now. You lackin'.", "phonetic_tips": ["Omite la 'g' final en tweaking y lackin.", "Une la pronunciación de 'they' y 'outside'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000002"),
        "title": "D2: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 2,
        "audio_url": _jdump({"lesson_title": "D2: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking right now. They outside the block waiting. You lackin' if you don't stay alert. We finna slide.", "formal_translation": "Formal: He is acting irrationally right now. They are outside... | Español: Él está actuando irracionalmente ahora. Ellos están afuera del bloque esperando. Estás desprevenido si no te mantienes alerta. Estamos a punto de ir.", "breakdown": [{"abbr": "tweaking", "meaning": "actuando irracionalmente (loco)"}, {"abbr": "they outside", "meaning": "ellos están afuera"}, {"abbr": "lackin'", "meaning": "desprevenido (con la guardia baja)"}, {"abbr": "finna slide", "meaning": "a punto de ir (atacar)"}], "grammar_notes": ["Zero Copula: Se omite el verbo 'to be' (ser/estar). Ej: 'He is tweaking' se convierte en 'He tweaking'."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end. We outside. He tweaking.", "exercise_text": "These girls ______ Sosa, O end or ______ end. We ______. He ______.", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "amar/adorar", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negativo", "distractor_options": ["know", "go"]}, {"position": 3, "correct_answers": ["outside"], "hint": "afuera", "distractor_options": ["inside", "away"]}, {"position": 4, "correct_answers": ["tweaking"], "hint": "actuando loco", "distractor_options": ["chilling", "sleeping"]}], "full_translation": "A estas chicas les encanta Sosa, es O block o nada. Estamos afuera. Él está actuando loco.", "grammar_notes": ["Contexto de Zero Copula en el drill típico de Chicago. (We [are] outside)."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside. You are unprepared.", "expected_drill_output": "He tweaking. They outside. You lackin.", "accepted_variants": ["He tweaking, they outside, you lackin", "He buggin, they outside, you lackin"], "evaluation_rubric": {"zero_copula": {"description": "Omite 'is' y 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Elimina 'is' y 'are' para formar la Zero Copula (omisión del verbo to be).", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside right now. You lackin'.", "phonetic_tips": ["Omite la 'g' final en tweaking y lackin.", "Une la pronunciación de 'they' y 'outside'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000003"),
        "title": "D3: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 3,
        "audio_url": _jdump({"lesson_title": "D3: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking right now. They outside the block waiting. You lackin' if you don't stay alert. We finna slide.", "formal_translation": "Formal: He is acting irrationally right now. They are outside... | Español: Él está actuando irracionalmente ahora. Ellos están afuera del bloque esperando. Estás desprevenido si no te mantienes alerta. Estamos a punto de ir.", "breakdown": [{"abbr": "tweaking", "meaning": "actuando irracionalmente (loco)"}, {"abbr": "they outside", "meaning": "ellos están afuera"}, {"abbr": "lackin'", "meaning": "desprevenido (con la guardia baja)"}, {"abbr": "finna slide", "meaning": "a punto de ir (atacar)"}], "grammar_notes": ["Zero Copula: Se omite el verbo 'to be' (ser/estar). Ej: 'He is tweaking' se convierte en 'He tweaking'."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end. We outside. He tweaking.", "exercise_text": "These girls ______ Sosa, O end or ______ end. We ______. He ______.", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "amar/adorar", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negativo", "distractor_options": ["know", "go"]}, {"position": 3, "correct_answers": ["outside"], "hint": "afuera", "distractor_options": ["inside", "away"]}, {"position": 4, "correct_answers": ["tweaking"], "hint": "actuando loco", "distractor_options": ["chilling", "sleeping"]}], "full_translation": "A estas chicas les encanta Sosa, es O block o nada. Estamos afuera. Él está actuando loco.", "grammar_notes": ["Contexto de Zero Copula en el drill típico de Chicago. (We [are] outside)."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside. You are unprepared.", "expected_drill_output": "He tweaking. They outside. You lackin.", "accepted_variants": ["He tweaking, they outside, you lackin", "He buggin, they outside, you lackin"], "evaluation_rubric": {"zero_copula": {"description": "Omite 'is' y 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Elimina 'is' y 'are' para formar la Zero Copula (omisión del verbo to be).", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside right now. You lackin'.", "phonetic_tips": ["Omite la 'g' final en tweaking y lackin.", "Une la pronunciación de 'they' y 'outside'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000004"),
        "title": "D4: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 4,
        "audio_url": _jdump({"lesson_title": "D4: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking right now. They outside the block waiting. You lackin' if you don't stay alert. We finna slide.", "formal_translation": "Formal: He is acting irrationally right now. They are outside... | Español: Él está actuando irracionalmente ahora. Ellos están afuera del bloque esperando. Estás desprevenido si no te mantienes alerta. Estamos a punto de ir.", "breakdown": [{"abbr": "tweaking", "meaning": "actuando irracionalmente (loco)"}, {"abbr": "they outside", "meaning": "ellos están afuera"}, {"abbr": "lackin'", "meaning": "desprevenido (con la guardia baja)"}, {"abbr": "finna slide", "meaning": "a punto de ir (atacar)"}], "grammar_notes": ["Zero Copula: Se omite el verbo 'to be' (ser/estar). Ej: 'He is tweaking' se convierte en 'He tweaking'."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end. We outside. He tweaking.", "exercise_text": "These girls ______ Sosa, O end or ______ end. We ______. He ______.", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "amar/adorar", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negativo", "distractor_options": ["know", "go"]}, {"position": 3, "correct_answers": ["outside"], "hint": "afuera", "distractor_options": ["inside", "away"]}, {"position": 4, "correct_answers": ["tweaking"], "hint": "actuando loco", "distractor_options": ["chilling", "sleeping"]}], "full_translation": "A estas chicas les encanta Sosa, es O block o nada. Estamos afuera. Él está actuando loco.", "grammar_notes": ["Contexto de Zero Copula en el drill típico de Chicago. (We [are] outside)."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside. You are unprepared.", "expected_drill_output": "He tweaking. They outside. You lackin.", "accepted_variants": ["He tweaking, they outside, you lackin", "He buggin, they outside, you lackin"], "evaluation_rubric": {"zero_copula": {"description": "Omite 'is' y 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Elimina 'is' y 'are' para formar la Zero Copula (omisión del verbo to be).", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside right now. You lackin'.", "phonetic_tips": ["Omite la 'g' final en tweaking y lackin.", "Une la pronunciación de 'they' y 'outside'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000005"),
        "title": "D5: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 5,
        "audio_url": _jdump({"lesson_title": "D5: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here. I ain't got no money for no games. Don't nobody know nothing.", "formal_translation": "Formal: Nobody is doing anything... | Español: Nadie está haciendo nada por aquí. No tengo dinero para juegos. Nadie sabe nada.", "breakdown": [{"abbr": "Ain't nobody doing nothing", "meaning": "Nadie está haciendo nada (Nótese la triple negación)"}, {"abbr": "ain't got no", "meaning": "no tengo ningún"}, {"abbr": "Don't nobody know nothing", "meaning": "Nadie sabe nada"}], "grammar_notes": ["Negative Concord (Doble Negación): Se usan múltiples negaciones para enfatizar, NO para cancelarse matemáticamente."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games. Ain't nobody sliding today.", "exercise_text": "I ______ got ______ time for ______ games. ______ nobody sliding today.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "no (do not)", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "ningún", "distractor_options": ["any", "some"]}, {"position": 3, "correct_answers": ["no"], "hint": "ningún", "distractor_options": ["any", "the"]}, {"position": 4, "correct_answers": ["Ain't", "aint"], "hint": "Nadie está", "distractor_options": ["Is", "Not"]}], "full_translation": "No tengo tiempo para juegos. Nadie va a atacar (slide) hoy.", "grammar_notes": ["Triple negación para dar fuerza: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything. I do not have any money.", "expected_drill_output": "Ain't nobody doing nothing. I ain't got no money.", "accepted_variants": ["Aint nobody doing nothing, I aint got no money"], "evaluation_rubric": {"negative_concord": {"description": "Usa ain't, nobody y nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Usa múltiples palabras negativas (ain't, nobody, nothing) en la misma oración para dar énfasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing. I ain't got no money.", "phonetic_tips": ["Haz énfasis y pon fuerza al pronunciar 'ain't' y 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000006"),
        "title": "D6: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 6,
        "audio_url": _jdump({"lesson_title": "D6: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here. I ain't got no money for no games. Don't nobody know nothing.", "formal_translation": "Formal: Nobody is doing anything... | Español: Nadie está haciendo nada por aquí. No tengo dinero para juegos. Nadie sabe nada.", "breakdown": [{"abbr": "Ain't nobody doing nothing", "meaning": "Nadie está haciendo nada (Nótese la triple negación)"}, {"abbr": "ain't got no", "meaning": "no tengo ningún"}, {"abbr": "Don't nobody know nothing", "meaning": "Nadie sabe nada"}], "grammar_notes": ["Negative Concord (Doble Negación): Se usan múltiples negaciones para enfatizar, NO para cancelarse matemáticamente."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games. Ain't nobody sliding today.", "exercise_text": "I ______ got ______ time for ______ games. ______ nobody sliding today.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "no (do not)", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "ningún", "distractor_options": ["any", "some"]}, {"position": 3, "correct_answers": ["no"], "hint": "ningún", "distractor_options": ["any", "the"]}, {"position": 4, "correct_answers": ["Ain't", "aint"], "hint": "Nadie está", "distractor_options": ["Is", "Not"]}], "full_translation": "No tengo tiempo para juegos. Nadie va a atacar (slide) hoy.", "grammar_notes": ["Triple negación para dar fuerza: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything. I do not have any money.", "expected_drill_output": "Ain't nobody doing nothing. I ain't got no money.", "accepted_variants": ["Aint nobody doing nothing, I aint got no money"], "evaluation_rubric": {"negative_concord": {"description": "Usa ain't, nobody y nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Usa múltiples palabras negativas (ain't, nobody, nothing) en la misma oración para dar énfasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing. I ain't got no money.", "phonetic_tips": ["Haz énfasis y pon fuerza al pronunciar 'ain't' y 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000007"),
        "title": "D7: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 7,
        "audio_url": _jdump({"lesson_title": "D7: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here. I ain't got no money for no games. Don't nobody know nothing.", "formal_translation": "Formal: Nobody is doing anything... | Español: Nadie está haciendo nada por aquí. No tengo dinero para juegos. Nadie sabe nada.", "breakdown": [{"abbr": "Ain't nobody doing nothing", "meaning": "Nadie está haciendo nada (Nótese la triple negación)"}, {"abbr": "ain't got no", "meaning": "no tengo ningún"}, {"abbr": "Don't nobody know nothing", "meaning": "Nadie sabe nada"}], "grammar_notes": ["Negative Concord (Doble Negación): Se usan múltiples negaciones para enfatizar, NO para cancelarse matemáticamente."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games. Ain't nobody sliding today.", "exercise_text": "I ______ got ______ time for ______ games. ______ nobody sliding today.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "no (do not)", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "ningún", "distractor_options": ["any", "some"]}, {"position": 3, "correct_answers": ["no"], "hint": "ningún", "distractor_options": ["any", "the"]}, {"position": 4, "correct_answers": ["Ain't", "aint"], "hint": "Nadie está", "distractor_options": ["Is", "Not"]}], "full_translation": "No tengo tiempo para juegos. Nadie va a atacar (slide) hoy.", "grammar_notes": ["Triple negación para dar fuerza: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything. I do not have any money.", "expected_drill_output": "Ain't nobody doing nothing. I ain't got no money.", "accepted_variants": ["Aint nobody doing nothing, I aint got no money"], "evaluation_rubric": {"negative_concord": {"description": "Usa ain't, nobody y nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Usa múltiples palabras negativas (ain't, nobody, nothing) en la misma oración para dar énfasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing. I ain't got no money.", "phonetic_tips": ["Haz énfasis y pon fuerza al pronunciar 'ain't' y 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000008"),
        "title": "D8: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 8,
        "audio_url": _jdump({"lesson_title": "D8: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here. I ain't got no money for no games. Don't nobody know nothing.", "formal_translation": "Formal: Nobody is doing anything... | Español: Nadie está haciendo nada por aquí. No tengo dinero para juegos. Nadie sabe nada.", "breakdown": [{"abbr": "Ain't nobody doing nothing", "meaning": "Nadie está haciendo nada (Nótese la triple negación)"}, {"abbr": "ain't got no", "meaning": "no tengo ningún"}, {"abbr": "Don't nobody know nothing", "meaning": "Nadie sabe nada"}], "grammar_notes": ["Negative Concord (Doble Negación): Se usan múltiples negaciones para enfatizar, NO para cancelarse matemáticamente."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games. Ain't nobody sliding today.", "exercise_text": "I ______ got ______ time for ______ games. ______ nobody sliding today.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "no (do not)", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "ningún", "distractor_options": ["any", "some"]}, {"position": 3, "correct_answers": ["no"], "hint": "ningún", "distractor_options": ["any", "the"]}, {"position": 4, "correct_answers": ["Ain't", "aint"], "hint": "Nadie está", "distractor_options": ["Is", "Not"]}], "full_translation": "No tengo tiempo para juegos. Nadie va a atacar (slide) hoy.", "grammar_notes": ["Triple negación para dar fuerza: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything. I do not have any money.", "expected_drill_output": "Ain't nobody doing nothing. I ain't got no money.", "accepted_variants": ["Aint nobody doing nothing, I aint got no money"], "evaluation_rubric": {"negative_concord": {"description": "Usa ain't, nobody y nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Usa múltiples palabras negativas (ain't, nobody, nothing) en la misma oración para dar énfasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing. I ain't got no money.", "phonetic_tips": ["Haz énfasis y pon fuerza al pronunciar 'ain't' y 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000009"),
        "title": "D9: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 9,
        "audio_url": _jdump({"lesson_title": "D9: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going with that blick? How they getting motion out here?", "formal_translation": "Formal: Why did you do that?... | Español: ¿Por qué hiciste eso? ¿A dónde va él con esa pistola? ¿Cómo están ganando éxito aquí?", "breakdown": [{"abbr": "Why you do", "meaning": "Por qué hiciste (omite 'did')"}, {"abbr": "Where he going", "meaning": "A dónde va (omite 'is')"}, {"abbr": "blick", "meaning": "pistola / arma"}, {"abbr": "motion", "meaning": "éxito / dinero / impulso"}], "grammar_notes": ["Inverted Syntax: Los verbos auxiliares (do, did, are) se omiten en las preguntas. El orden de las palabras se mantiene igual."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that? Why he capping about his motion?", "exercise_text": "______ you going with that? ______ he capping about his ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Palabra de pregunta (Dónde)", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["Why"], "hint": "Razón (Por qué)", "distractor_options": ["Who", "How"]}, {"position": 3, "correct_answers": ["motion"], "hint": "éxito/dinero", "distractor_options": ["money", "cars"]}], "full_translation": "¿A dónde vas con eso? ¿Por qué él está mintiendo sobre su éxito?", "grammar_notes": ["Se omite 'are' e 'is' en las preguntas directas."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that? Where is he going?", "expected_drill_output": "Why you do that? Where he going?", "accepted_variants": ["Why you do that, where he going", "Why you do that? Where he going with that"], "evaluation_rubric": {"drop_aux": {"description": "Omite 'did' y 'is'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Elimina el verbo auxiliar (do/did/is/are) para hacer la pregunta de forma nativa.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that? Where he going with that blick?", "phonetic_tips": ["Sube el tono de voz al final de la oración para indicar que es una pregunta."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000010"),
        "title": "D10: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 10,
        "audio_url": _jdump({"lesson_title": "D10: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going with that blick? How they getting motion out here?", "formal_translation": "Formal: Why did you do that?... | Español: ¿Por qué hiciste eso? ¿A dónde va él con esa pistola? ¿Cómo están ganando éxito aquí?", "breakdown": [{"abbr": "Why you do", "meaning": "Por qué hiciste (omite 'did')"}, {"abbr": "Where he going", "meaning": "A dónde va (omite 'is')"}, {"abbr": "blick", "meaning": "pistola / arma"}, {"abbr": "motion", "meaning": "éxito / dinero / impulso"}], "grammar_notes": ["Inverted Syntax: Los verbos auxiliares (do, did, are) se omiten en las preguntas. El orden de las palabras se mantiene igual."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that? Why he capping about his motion?", "exercise_text": "______ you going with that? ______ he capping about his ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Palabra de pregunta (Dónde)", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["Why"], "hint": "Razón (Por qué)", "distractor_options": ["Who", "How"]}, {"position": 3, "correct_answers": ["motion"], "hint": "éxito/dinero", "distractor_options": ["money", "cars"]}], "full_translation": "¿A dónde vas con eso? ¿Por qué él está mintiendo sobre su éxito?", "grammar_notes": ["Se omite 'are' e 'is' en las preguntas directas."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that? Where is he going?", "expected_drill_output": "Why you do that? Where he going?", "accepted_variants": ["Why you do that, where he going", "Why you do that? Where he going with that"], "evaluation_rubric": {"drop_aux": {"description": "Omite 'did' y 'is'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Elimina el verbo auxiliar (do/did/is/are) para hacer la pregunta de forma nativa.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that? Where he going with that blick?", "phonetic_tips": ["Sube el tono de voz al final de la oración para indicar que es una pregunta."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000011"),
        "title": "D11: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 11,
        "audio_url": _jdump({"lesson_title": "D11: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going with that blick? How they getting motion out here?", "formal_translation": "Formal: Why did you do that?... | Español: ¿Por qué hiciste eso? ¿A dónde va él con esa pistola? ¿Cómo están ganando éxito aquí?", "breakdown": [{"abbr": "Why you do", "meaning": "Por qué hiciste (omite 'did')"}, {"abbr": "Where he going", "meaning": "A dónde va (omite 'is')"}, {"abbr": "blick", "meaning": "pistola / arma"}, {"abbr": "motion", "meaning": "éxito / dinero / impulso"}], "grammar_notes": ["Inverted Syntax: Los verbos auxiliares (do, did, are) se omiten en las preguntas. El orden de las palabras se mantiene igual."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that? Why he capping about his motion?", "exercise_text": "______ you going with that? ______ he capping about his ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Palabra de pregunta (Dónde)", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["Why"], "hint": "Razón (Por qué)", "distractor_options": ["Who", "How"]}, {"position": 3, "correct_answers": ["motion"], "hint": "éxito/dinero", "distractor_options": ["money", "cars"]}], "full_translation": "¿A dónde vas con eso? ¿Por qué él está mintiendo sobre su éxito?", "grammar_notes": ["Se omite 'are' e 'is' en las preguntas directas."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that? Where is he going?", "expected_drill_output": "Why you do that? Where he going?", "accepted_variants": ["Why you do that, where he going", "Why you do that? Where he going with that"], "evaluation_rubric": {"drop_aux": {"description": "Omite 'did' y 'is'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Elimina el verbo auxiliar (do/did/is/are) para hacer la pregunta de forma nativa.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that? Where he going with that blick?", "phonetic_tips": ["Sube el tono de voz al final de la oración para indicar que es una pregunta."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000012"),
        "title": "D12: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 12,
        "audio_url": _jdump({"lesson_title": "D12: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going with that blick? How they getting motion out here?", "formal_translation": "Formal: Why did you do that?... | Español: ¿Por qué hiciste eso? ¿A dónde va él con esa pistola? ¿Cómo están ganando éxito aquí?", "breakdown": [{"abbr": "Why you do", "meaning": "Por qué hiciste (omite 'did')"}, {"abbr": "Where he going", "meaning": "A dónde va (omite 'is')"}, {"abbr": "blick", "meaning": "pistola / arma"}, {"abbr": "motion", "meaning": "éxito / dinero / impulso"}], "grammar_notes": ["Inverted Syntax: Los verbos auxiliares (do, did, are) se omiten en las preguntas. El orden de las palabras se mantiene igual."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that? Why he capping about his motion?", "exercise_text": "______ you going with that? ______ he capping about his ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Palabra de pregunta (Dónde)", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["Why"], "hint": "Razón (Por qué)", "distractor_options": ["Who", "How"]}, {"position": 3, "correct_answers": ["motion"], "hint": "éxito/dinero", "distractor_options": ["money", "cars"]}], "full_translation": "¿A dónde vas con eso? ¿Por qué él está mintiendo sobre su éxito?", "grammar_notes": ["Se omite 'are' e 'is' en las preguntas directas."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that? Where is he going?", "expected_drill_output": "Why you do that? Where he going?", "accepted_variants": ["Why you do that, where he going", "Why you do that? Where he going with that"], "evaluation_rubric": {"drop_aux": {"description": "Omite 'did' y 'is'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Elimina el verbo auxiliar (do/did/is/are) para hacer la pregunta de forma nativa.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that? Where he going with that blick?", "phonetic_tips": ["Sube el tono de voz al final de la oración para indicar que es una pregunta."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000013"),
        "title": "D13: Territory (Possessives)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 13,
        "audio_url": _jdump({"lesson_title": "D13: Territory (Possessives)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "They outside they house. We taking they spot. They lost they motion completely.", "formal_translation": "Formal: They are outside their house... | Español: Ellos están afuera de su casa. Estamos tomando su lugar. Perdieron su impulso por completo.", "breakdown": [{"abbr": "they house", "meaning": "su casa (de ellos)"}, {"abbr": "they spot", "meaning": "su lugar (de ellos)"}, {"abbr": "they motion", "meaning": "su éxito/impulso (de ellos)"}], "grammar_notes": ["Sustitución de Posesivo: Se usa 'they' (ellos) en lugar de 'their' (su de ellos) para indicar posesión."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Kay Flock", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "gGJS8W9emac", "original_bar": "They all in they feelings. They lost they motion.", "exercise_text": "They all in ______ feelings. They lost ______ ______.", "blanks": [{"position": 1, "correct_answers": ["they"], "hint": "su (de ellos)", "distractor_options": ["their", "there"]}, {"position": 2, "correct_answers": ["they"], "hint": "su (de ellos)", "distractor_options": ["their", "the"]}, {"position": 3, "correct_answers": ["motion"], "hint": "impulso/éxito", "distractor_options": ["money", "spot"]}], "full_translation": "Están todos metidos en sus sentimientos. Perdieron su impulso.", "grammar_notes": ["Se usa 'they feelings' en lugar del inglés estándar 'their feelings'."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "They are outside their house. They lost their momentum.", "expected_drill_output": "They outside they house. They lost they motion.", "accepted_variants": ["They outside they house, they lost they motion"], "evaluation_rubric": {"possessive": {"description": "Usa 'they' en lugar de 'their'", "points": 100, "example": "they house"}}, "grammar_explanation": "Reemplaza el posesivo 'their' (estándar) simplemente por 'they'.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "They outside they house. They lost they motion.", "phonetic_tips": ["Une suavemente la pronunciación de 'they' con la siguiente palabra sin pausas."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000014"),
        "title": "D14: Territory (Possessives)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 14,
        "audio_url": _jdump({"lesson_title": "D14: Territory (Possessives)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "They outside they house. We taking they spot. They lost they motion completely.", "formal_translation": "Formal: They are outside their house... | Español: Ellos están afuera de su casa. Estamos tomando su lugar. Perdieron su impulso por completo.", "breakdown": [{"abbr": "they house", "meaning": "su casa (de ellos)"}, {"abbr": "they spot", "meaning": "su lugar (de ellos)"}, {"abbr": "they motion", "meaning": "su éxito/impulso (de ellos)"}], "grammar_notes": ["Sustitución de Posesivo: Se usa 'they' (ellos) en lugar de 'their' (su de ellos) para indicar posesión."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Kay Flock", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "gGJS8W9emac", "original_bar": "They all in they feelings. They lost they motion.", "exercise_text": "They all in ______ feelings. They lost ______ ______.", "blanks": [{"position": 1, "correct_answers": ["they"], "hint": "su (de ellos)", "distractor_options": ["their", "there"]}, {"position": 2, "correct_answers": ["they"], "hint": "su (de ellos)", "distractor_options": ["their", "the"]}, {"position": 3, "correct_answers": ["motion"], "hint": "impulso/éxito", "distractor_options": ["money", "spot"]}], "full_translation": "Están todos metidos en sus sentimientos. Perdieron su impulso.", "grammar_notes": ["Se usa 'they feelings' en lugar del inglés estándar 'their feelings'."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "They are outside their house. They lost their momentum.", "expected_drill_output": "They outside they house. They lost they motion.", "accepted_variants": ["They outside they house, they lost they motion"], "evaluation_rubric": {"possessive": {"description": "Usa 'they' en lugar de 'their'", "points": 100, "example": "they house"}}, "grammar_explanation": "Reemplaza el posesivo 'their' (estándar) simplemente por 'they'.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "They outside they house. They lost they motion.", "phonetic_tips": ["Une suavemente la pronunciación de 'they' con la siguiente palabra sin pausas."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000015"),
        "title": "D15: Territory (Possessives)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 15,
        "audio_url": _jdump({"lesson_title": "D15: Territory (Possessives)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "They outside they house. We taking they spot. They lost they motion completely.", "formal_translation": "Formal: They are outside their house... | Español: Ellos están afuera de su casa. Estamos tomando su lugar. Perdieron su impulso por completo.", "breakdown": [{"abbr": "they house", "meaning": "su casa (de ellos)"}, {"abbr": "they spot", "meaning": "su lugar (de ellos)"}, {"abbr": "they motion", "meaning": "su éxito/impulso (de ellos)"}], "grammar_notes": ["Sustitución de Posesivo: Se usa 'they' (ellos) en lugar de 'their' (su de ellos) para indicar posesión."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Kay Flock", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "gGJS8W9emac", "original_bar": "They all in they feelings. They lost they motion.", "exercise_text": "They all in ______ feelings. They lost ______ ______.", "blanks": [{"position": 1, "correct_answers": ["they"], "hint": "su (de ellos)", "distractor_options": ["their", "there"]}, {"position": 2, "correct_answers": ["they"], "hint": "su (de ellos)", "distractor_options": ["their", "the"]}, {"position": 3, "correct_answers": ["motion"], "hint": "impulso/éxito", "distractor_options": ["money", "spot"]}], "full_translation": "Están todos metidos en sus sentimientos. Perdieron su impulso.", "grammar_notes": ["Se usa 'they feelings' en lugar del inglés estándar 'their feelings'."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "They are outside their house. They lost their momentum.", "expected_drill_output": "They outside they house. They lost they motion.", "accepted_variants": ["They outside they house, they lost they motion"], "evaluation_rubric": {"possessive": {"description": "Usa 'they' en lugar de 'their'", "points": 100, "example": "they house"}}, "grammar_explanation": "Reemplaza el posesivo 'their' (estándar) simplemente por 'they'.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "They outside they house. They lost they motion.", "phonetic_tips": ["Une suavemente la pronunciación de 'they' con la siguiente palabra sin pausas."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
]

async def _reset_content(session: AsyncSession) -> None:
    print("  → Borrando lecciones existentes...")
    await session.execute(text("DELETE FROM lessons"))
    print("  → Borrando vocabulario existente...")
    await session.execute(text("DELETE FROM vocabulary_items"))
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
                "level_band": "B1",
            },
        )
    await session.commit()
    print(f"  ✓ {len(VOCABULARY_ITEMS)} términos insertados.")

async def _seed_lessons(session: AsyncSession) -> None:
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
    print(f"\n  │  vocabulary_items : {vocab_count:<22} │")
    print(f"  │  lessons          : {lesson_count:<22} │")

async def main() -> None:
    reset_mode = "--reset" in sys.argv
    print("\n🎤  Drillingo — Database Seeder")
    async with SessionLocal() as session:
        if reset_mode:
            await _reset_content(session)
        await _seed_vocabulary(session)
        await _seed_lessons(session)
        await _verify(session)
    print("\n✅  Seed completado exitosamente.\n")

if __name__ == "__main__":
    asyncio.run(main())
