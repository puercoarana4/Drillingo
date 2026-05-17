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
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000001"), "term": "Tweaking", "definition": "Acting irrationally or panicking.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000002"), "term": "Opp", "definition": "Enemy or opposition.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000003"), "term": "Finna", "definition": "About to / going to.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000004"), "term": "Lackin'", "definition": "Caught unprepared.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000005"), "term": "Slide", "definition": "To drive to a location to confront someone.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000006"), "term": "Blick", "definition": "A firearm.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000007"), "term": "Drop", "definition": "Location / address.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000008"), "term": "Merch it", "definition": "Swear on it.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
]

ALL_LESSONS = [
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000001"),
        "title": "D1: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 1,
        "audio_url": _jdump({"lesson_title": "D1: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking, they outside right now.", "formal_translation": "He is acting irrationally. They are outside right now.", "breakdown": [{"abbr": "tweaking", "meaning": "acting irrationally"}, {"abbr": "they outside", "meaning": "they are outside"}], "grammar_notes": ["Zero Copula: The verb 'to be' is omitted when acting as a linking verb."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end", "exercise_text": "These girls ______ Sosa, O end or ______ end", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "adore", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negative", "distractor_options": ["know", "go"]}], "full_translation": "These girls love Sosa, it is O block or nothing.", "grammar_notes": ["Zero Copula context in typical Chicago drill."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside.", "expected_drill_output": "He tweaking, they outside", "accepted_variants": ["He tweaking they outside"], "evaluation_rubric": {"zero_copula": {"description": "Omits 'is' and 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Drop 'is' and 'are' to form the Zero Copula.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside.", "phonetic_tips": ["Drop the 'g' in tweaking.", "Blend they and outside."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000002"),
        "title": "D2: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 2,
        "audio_url": _jdump({"lesson_title": "D2: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking, they outside right now.", "formal_translation": "He is acting irrationally. They are outside right now.", "breakdown": [{"abbr": "tweaking", "meaning": "acting irrationally"}, {"abbr": "they outside", "meaning": "they are outside"}], "grammar_notes": ["Zero Copula: The verb 'to be' is omitted when acting as a linking verb."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end", "exercise_text": "These girls ______ Sosa, O end or ______ end", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "adore", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negative", "distractor_options": ["know", "go"]}], "full_translation": "These girls love Sosa, it is O block or nothing.", "grammar_notes": ["Zero Copula context in typical Chicago drill."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside.", "expected_drill_output": "He tweaking, they outside", "accepted_variants": ["He tweaking they outside"], "evaluation_rubric": {"zero_copula": {"description": "Omits 'is' and 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Drop 'is' and 'are' to form the Zero Copula.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside.", "phonetic_tips": ["Drop the 'g' in tweaking.", "Blend they and outside."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000003"),
        "title": "D3: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 3,
        "audio_url": _jdump({"lesson_title": "D3: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking, they outside right now.", "formal_translation": "He is acting irrationally. They are outside right now.", "breakdown": [{"abbr": "tweaking", "meaning": "acting irrationally"}, {"abbr": "they outside", "meaning": "they are outside"}], "grammar_notes": ["Zero Copula: The verb 'to be' is omitted when acting as a linking verb."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end", "exercise_text": "These girls ______ Sosa, O end or ______ end", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "adore", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negative", "distractor_options": ["know", "go"]}], "full_translation": "These girls love Sosa, it is O block or nothing.", "grammar_notes": ["Zero Copula context in typical Chicago drill."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside.", "expected_drill_output": "He tweaking, they outside", "accepted_variants": ["He tweaking they outside"], "evaluation_rubric": {"zero_copula": {"description": "Omits 'is' and 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Drop 'is' and 'are' to form the Zero Copula.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside.", "phonetic_tips": ["Drop the 'g' in tweaking.", "Blend they and outside."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000004"),
        "title": "D4: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 4,
        "audio_url": _jdump({"lesson_title": "D4: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking, they outside right now.", "formal_translation": "He is acting irrationally. They are outside right now.", "breakdown": [{"abbr": "tweaking", "meaning": "acting irrationally"}, {"abbr": "they outside", "meaning": "they are outside"}], "grammar_notes": ["Zero Copula: The verb 'to be' is omitted when acting as a linking verb."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end", "exercise_text": "These girls ______ Sosa, O end or ______ end", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "adore", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negative", "distractor_options": ["know", "go"]}], "full_translation": "These girls love Sosa, it is O block or nothing.", "grammar_notes": ["Zero Copula context in typical Chicago drill."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside.", "expected_drill_output": "He tweaking, they outside", "accepted_variants": ["He tweaking they outside"], "evaluation_rubric": {"zero_copula": {"description": "Omits 'is' and 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Drop 'is' and 'are' to form the Zero Copula.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside.", "phonetic_tips": ["Drop the 'g' in tweaking.", "Blend they and outside."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000005"),
        "title": "D5: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 5,
        "audio_url": _jdump({"lesson_title": "D5: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here.", "formal_translation": "Nobody is doing anything around here.", "breakdown": [{"abbr": "Ain't nobody", "meaning": "Nobody is"}, {"abbr": "nothing", "meaning": "anything"}], "grammar_notes": ["Negative Concord: Multiple negatives are used to emphasize negation, not cancel it."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games.", "exercise_text": "I ______ got ______ time for no games.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "do not", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "some"]}], "full_translation": "I do not have any time for any games.", "grammar_notes": ["Triple negation: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything.", "expected_drill_output": "Ain't nobody doing nothing", "accepted_variants": ["Aint nobody doing nothing"], "evaluation_rubric": {"negative_concord": {"description": "Uses ain't, nobody, and nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Use multiple negatives for emphasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing.", "phonetic_tips": ["Stress 'ain't' and 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000006"),
        "title": "D6: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 6,
        "audio_url": _jdump({"lesson_title": "D6: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here.", "formal_translation": "Nobody is doing anything around here.", "breakdown": [{"abbr": "Ain't nobody", "meaning": "Nobody is"}, {"abbr": "nothing", "meaning": "anything"}], "grammar_notes": ["Negative Concord: Multiple negatives are used to emphasize negation, not cancel it."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games.", "exercise_text": "I ______ got ______ time for no games.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "do not", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "some"]}], "full_translation": "I do not have any time for any games.", "grammar_notes": ["Triple negation: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything.", "expected_drill_output": "Ain't nobody doing nothing", "accepted_variants": ["Aint nobody doing nothing"], "evaluation_rubric": {"negative_concord": {"description": "Uses ain't, nobody, and nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Use multiple negatives for emphasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing.", "phonetic_tips": ["Stress 'ain't' and 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000007"),
        "title": "D7: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 7,
        "audio_url": _jdump({"lesson_title": "D7: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here.", "formal_translation": "Nobody is doing anything around here.", "breakdown": [{"abbr": "Ain't nobody", "meaning": "Nobody is"}, {"abbr": "nothing", "meaning": "anything"}], "grammar_notes": ["Negative Concord: Multiple negatives are used to emphasize negation, not cancel it."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games.", "exercise_text": "I ______ got ______ time for no games.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "do not", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "some"]}], "full_translation": "I do not have any time for any games.", "grammar_notes": ["Triple negation: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything.", "expected_drill_output": "Ain't nobody doing nothing", "accepted_variants": ["Aint nobody doing nothing"], "evaluation_rubric": {"negative_concord": {"description": "Uses ain't, nobody, and nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Use multiple negatives for emphasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing.", "phonetic_tips": ["Stress 'ain't' and 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000008"),
        "title": "D8: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 8,
        "audio_url": _jdump({"lesson_title": "D8: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here.", "formal_translation": "Nobody is doing anything around here.", "breakdown": [{"abbr": "Ain't nobody", "meaning": "Nobody is"}, {"abbr": "nothing", "meaning": "anything"}], "grammar_notes": ["Negative Concord: Multiple negatives are used to emphasize negation, not cancel it."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games.", "exercise_text": "I ______ got ______ time for no games.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "do not", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "some"]}], "full_translation": "I do not have any time for any games.", "grammar_notes": ["Triple negation: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything.", "expected_drill_output": "Ain't nobody doing nothing", "accepted_variants": ["Aint nobody doing nothing"], "evaluation_rubric": {"negative_concord": {"description": "Uses ain't, nobody, and nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Use multiple negatives for emphasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing.", "phonetic_tips": ["Stress 'ain't' and 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000009"),
        "title": "D9: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 9,
        "audio_url": _jdump({"lesson_title": "D9: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going?", "formal_translation": "Why did you do that? Where is he going?", "breakdown": [{"abbr": "Why you do", "meaning": "Why did you do"}], "grammar_notes": ["Inverted Syntax: Auxiliary verbs (do, did, are) are omitted in questions."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that?", "exercise_text": "______ you going with ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Question word", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["that"], "hint": "Pronoun", "distractor_options": ["this", "it"]}], "full_translation": "Where are you going with that?", "grammar_notes": ["Omits 'are' in the question."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that?", "expected_drill_output": "Why you do that?", "accepted_variants": ["Why you do that"], "evaluation_rubric": {"drop_aux": {"description": "Drops 'did'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Drop the auxiliary verb to form the question.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that?", "phonetic_tips": ["Rise your pitch at the end."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000010"),
        "title": "D10: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 10,
        "audio_url": _jdump({"lesson_title": "D10: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going?", "formal_translation": "Why did you do that? Where is he going?", "breakdown": [{"abbr": "Why you do", "meaning": "Why did you do"}], "grammar_notes": ["Inverted Syntax: Auxiliary verbs (do, did, are) are omitted in questions."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that?", "exercise_text": "______ you going with ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Question word", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["that"], "hint": "Pronoun", "distractor_options": ["this", "it"]}], "full_translation": "Where are you going with that?", "grammar_notes": ["Omits 'are' in the question."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that?", "expected_drill_output": "Why you do that?", "accepted_variants": ["Why you do that"], "evaluation_rubric": {"drop_aux": {"description": "Drops 'did'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Drop the auxiliary verb to form the question.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that?", "phonetic_tips": ["Rise your pitch at the end."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000011"),
        "title": "D11: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 11,
        "audio_url": _jdump({"lesson_title": "D11: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going?", "formal_translation": "Why did you do that? Where is he going?", "breakdown": [{"abbr": "Why you do", "meaning": "Why did you do"}], "grammar_notes": ["Inverted Syntax: Auxiliary verbs (do, did, are) are omitted in questions."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that?", "exercise_text": "______ you going with ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Question word", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["that"], "hint": "Pronoun", "distractor_options": ["this", "it"]}], "full_translation": "Where are you going with that?", "grammar_notes": ["Omits 'are' in the question."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that?", "expected_drill_output": "Why you do that?", "accepted_variants": ["Why you do that"], "evaluation_rubric": {"drop_aux": {"description": "Drops 'did'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Drop the auxiliary verb to form the question.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that?", "phonetic_tips": ["Rise your pitch at the end."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000012"),
        "title": "D12: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 12,
        "audio_url": _jdump({"lesson_title": "D12: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going?", "formal_translation": "Why did you do that? Where is he going?", "breakdown": [{"abbr": "Why you do", "meaning": "Why did you do"}], "grammar_notes": ["Inverted Syntax: Auxiliary verbs (do, did, are) are omitted in questions."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that?", "exercise_text": "______ you going with ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Question word", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["that"], "hint": "Pronoun", "distractor_options": ["this", "it"]}], "full_translation": "Where are you going with that?", "grammar_notes": ["Omits 'are' in the question."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that?", "expected_drill_output": "Why you do that?", "accepted_variants": ["Why you do that"], "evaluation_rubric": {"drop_aux": {"description": "Drops 'did'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Drop the auxiliary verb to form the question.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that?", "phonetic_tips": ["Rise your pitch at the end."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000013"),
        "title": "D13: Territory (Possessives)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 13,
        "audio_url": _jdump({"lesson_title": "D13: Territory (Possessives)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "They outside they house.", "formal_translation": "They are outside their house.", "breakdown": [{"abbr": "they house", "meaning": "their house"}], "grammar_notes": ["Possessive Substitution: 'They' is used instead of 'their' for possession."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Kay Flock", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "gGJS8W9emac", "original_bar": "They all in they feelings.", "exercise_text": "They all in ______ feelings.", "blanks": [{"position": 1, "correct_answers": ["they"], "hint": "their", "distractor_options": ["their", "there"]}], "full_translation": "They are all in their feelings.", "grammar_notes": ["'they feelings' instead of 'their feelings'."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "They are outside their house.", "expected_drill_output": "They outside they house", "accepted_variants": ["They outside they house."], "evaluation_rubric": {"possessive": {"description": "Uses 'they' instead of 'their'", "points": 100, "example": "they house"}}, "grammar_explanation": "Replace 'their' with 'they'.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "They outside they house.", "phonetic_tips": ["Blend 'they' and 'outside'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000014"),
        "title": "D14: Territory (Possessives)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 14,
        "audio_url": _jdump({"lesson_title": "D14: Territory (Possessives)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "They outside they house.", "formal_translation": "They are outside their house.", "breakdown": [{"abbr": "they house", "meaning": "their house"}], "grammar_notes": ["Possessive Substitution: 'They' is used instead of 'their' for possession."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Kay Flock", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "gGJS8W9emac", "original_bar": "They all in they feelings.", "exercise_text": "They all in ______ feelings.", "blanks": [{"position": 1, "correct_answers": ["they"], "hint": "their", "distractor_options": ["their", "there"]}], "full_translation": "They are all in their feelings.", "grammar_notes": ["'they feelings' instead of 'their feelings'."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "They are outside their house.", "expected_drill_output": "They outside they house", "accepted_variants": ["They outside they house."], "evaluation_rubric": {"possessive": {"description": "Uses 'they' instead of 'their'", "points": 100, "example": "they house"}}, "grammar_explanation": "Replace 'their' with 'they'.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "They outside they house.", "phonetic_tips": ["Blend 'they' and 'outside'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000015"),
        "title": "D15: Territory (Possessives)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 15,
        "audio_url": _jdump({"lesson_title": "D15: Territory (Possessives)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "They outside they house.", "formal_translation": "They are outside their house.", "breakdown": [{"abbr": "they house", "meaning": "their house"}], "grammar_notes": ["Possessive Substitution: 'They' is used instead of 'their' for possession."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Kay Flock", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "gGJS8W9emac", "original_bar": "They all in they feelings.", "exercise_text": "They all in ______ feelings.", "blanks": [{"position": 1, "correct_answers": ["they"], "hint": "their", "distractor_options": ["their", "there"]}], "full_translation": "They are all in their feelings.", "grammar_notes": ["'they feelings' instead of 'their feelings'."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "They are outside their house.", "expected_drill_output": "They outside they house", "accepted_variants": ["They outside they house."], "evaluation_rubric": {"possessive": {"description": "Uses 'they' instead of 'their'", "points": 100, "example": "they house"}}, "grammar_explanation": "Replace 'their' with 'they'.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "They outside they house.", "phonetic_tips": ["Blend 'they' and 'outside'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
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
