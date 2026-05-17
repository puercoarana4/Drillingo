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
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000001"), "term": "Crash out", "definition": "To lose control and act recklessly.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000002"), "term": "Slide", "definition": "To drive to a location to confront someone.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000003"), "term": "Flock", "definition": "To shoot or to rob someone.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000004"), "term": "Tweaking", "definition": "To act irrationally or panic.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000005"), "term": "Cap", "definition": "To lie. 'No cap' means I am not lying.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000006"), "term": "Snake", "definition": "To betray someone.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000007"), "term": "Lurk", "definition": "To wait out of sight.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000008"), "term": "Drop a dime", "definition": "To inform the police.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000009"), "term": "Wocky", "definition": "Strange or suspicious.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000010"), "term": "Lackin'", "definition": "Caught unprepared.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000011"), "term": "Fanned out", "definition": "Acting obsessed.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000012"), "term": "Valid", "definition": "Acceptable or good.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000013"), "term": "Dayroom", "definition": "Someone who is unreliable.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000014"), "term": "On go", "definition": "Ready for action.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000015"), "term": "Opp", "definition": "Enemy or opposition.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000016"), "term": "12", "definition": "The police.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000017"), "term": "Blick", "definition": "Firearm / Gun.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000018"), "term": "Drop", "definition": "Location / address.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000019"), "term": "Motion", "definition": "Having momentum or success.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000020"), "term": "Function", "definition": "A party or gathering.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000021"), "term": "Merch it", "definition": "Swear on it.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000022"), "term": "Expeditiously", "definition": "Immediately and quickly.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "C1"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000023"), "term": "Word to my dead", "definition": "I swear on my deceased relatives.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B2"},
    {"id": uuid.UUID("11111111-0000-0000-0000-000000000024"), "term": "Finna", "definition": "About to / going to.", "example_sentence": "", "dialect_segment": "midwest", "level_band": "B1"},
]

ALL_LESSONS = [
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000001"),
        "title": "D1: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 1,
        "audio_url": _jdump({"lesson_title": "D1: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking right now. They outside the block waiting. You lackin' if you don't stay alert. We finna slide.", "formal_translation": "He is acting irrationally right now. They are outside the neighborhood waiting. You are unprepared if you do not stay alert. We are about to go.", "breakdown": [{"abbr": "tweaking", "meaning": "acting irrationally"}, {"abbr": "they outside", "meaning": "they are outside"}, {"abbr": "lackin'", "meaning": "unprepared"}, {"abbr": "finna slide", "meaning": "about to drive over"}], "grammar_notes": ["Zero Copula: The verb 'to be' is omitted. 'He is tweaking' -> 'He tweaking'."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end. We outside. He tweaking.", "exercise_text": "These girls ______ Sosa, O end or ______ end. We ______. He ______.", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "adore", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negative", "distractor_options": ["know", "go"]}, {"position": 3, "correct_answers": ["outside"], "hint": "outdoors", "distractor_options": ["inside", "away"]}, {"position": 4, "correct_answers": ["tweaking"], "hint": "acting crazy", "distractor_options": ["chilling", "sleeping"]}], "full_translation": "These girls love Sosa, it is O block or nothing. We are outside. He is acting crazy.", "grammar_notes": ["Zero Copula context in typical Chicago drill."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside. You are unprepared.", "expected_drill_output": "He tweaking. They outside. You lackin.", "accepted_variants": ["He tweaking, they outside, you lackin", "He buggin, they outside, you lackin"], "evaluation_rubric": {"zero_copula": {"description": "Omits 'is' and 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Drop 'is' and 'are' to form the Zero Copula.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside right now. You lackin'.", "phonetic_tips": ["Drop the 'g' in tweaking and lackin.", "Blend they and outside."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000002"),
        "title": "D2: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 2,
        "audio_url": _jdump({"lesson_title": "D2: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking right now. They outside the block waiting. You lackin' if you don't stay alert. We finna slide.", "formal_translation": "He is acting irrationally right now. They are outside the neighborhood waiting. You are unprepared if you do not stay alert. We are about to go.", "breakdown": [{"abbr": "tweaking", "meaning": "acting irrationally"}, {"abbr": "they outside", "meaning": "they are outside"}, {"abbr": "lackin'", "meaning": "unprepared"}, {"abbr": "finna slide", "meaning": "about to drive over"}], "grammar_notes": ["Zero Copula: The verb 'to be' is omitted. 'He is tweaking' -> 'He tweaking'."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end. We outside. He tweaking.", "exercise_text": "These girls ______ Sosa, O end or ______ end. We ______. He ______.", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "adore", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negative", "distractor_options": ["know", "go"]}, {"position": 3, "correct_answers": ["outside"], "hint": "outdoors", "distractor_options": ["inside", "away"]}, {"position": 4, "correct_answers": ["tweaking"], "hint": "acting crazy", "distractor_options": ["chilling", "sleeping"]}], "full_translation": "These girls love Sosa, it is O block or nothing. We are outside. He is acting crazy.", "grammar_notes": ["Zero Copula context in typical Chicago drill."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside. You are unprepared.", "expected_drill_output": "He tweaking. They outside. You lackin.", "accepted_variants": ["He tweaking, they outside, you lackin", "He buggin, they outside, you lackin"], "evaluation_rubric": {"zero_copula": {"description": "Omits 'is' and 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Drop 'is' and 'are' to form the Zero Copula.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside right now. You lackin'.", "phonetic_tips": ["Drop the 'g' in tweaking and lackin.", "Blend they and outside."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000003"),
        "title": "D3: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 3,
        "audio_url": _jdump({"lesson_title": "D3: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking right now. They outside the block waiting. You lackin' if you don't stay alert. We finna slide.", "formal_translation": "He is acting irrationally right now. They are outside the neighborhood waiting. You are unprepared if you do not stay alert. We are about to go.", "breakdown": [{"abbr": "tweaking", "meaning": "acting irrationally"}, {"abbr": "they outside", "meaning": "they are outside"}, {"abbr": "lackin'", "meaning": "unprepared"}, {"abbr": "finna slide", "meaning": "about to drive over"}], "grammar_notes": ["Zero Copula: The verb 'to be' is omitted. 'He is tweaking' -> 'He tweaking'."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end. We outside. He tweaking.", "exercise_text": "These girls ______ Sosa, O end or ______ end. We ______. He ______.", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "adore", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negative", "distractor_options": ["know", "go"]}, {"position": 3, "correct_answers": ["outside"], "hint": "outdoors", "distractor_options": ["inside", "away"]}, {"position": 4, "correct_answers": ["tweaking"], "hint": "acting crazy", "distractor_options": ["chilling", "sleeping"]}], "full_translation": "These girls love Sosa, it is O block or nothing. We are outside. He is acting crazy.", "grammar_notes": ["Zero Copula context in typical Chicago drill."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside. You are unprepared.", "expected_drill_output": "He tweaking. They outside. You lackin.", "accepted_variants": ["He tweaking, they outside, you lackin", "He buggin, they outside, you lackin"], "evaluation_rubric": {"zero_copula": {"description": "Omits 'is' and 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Drop 'is' and 'are' to form the Zero Copula.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside right now. You lackin'.", "phonetic_tips": ["Drop the 'g' in tweaking and lackin.", "Blend they and outside."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000004"),
        "title": "D4: The Chicago Setup (Zero Copula)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 4,
        "audio_url": _jdump({"lesson_title": "D4: The Chicago Setup (Zero Copula)", "dialect_focus": "Chicago", "modules": {"reading": {"module_type": "reading", "dialect_focus": "Chicago", "raw_text": "He tweaking right now. They outside the block waiting. You lackin' if you don't stay alert. We finna slide.", "formal_translation": "He is acting irrationally right now. They are outside the neighborhood waiting. You are unprepared if you do not stay alert. We are about to go.", "breakdown": [{"abbr": "tweaking", "meaning": "acting irrationally"}, {"abbr": "they outside", "meaning": "they are outside"}, {"abbr": "lackin'", "meaning": "unprepared"}, {"abbr": "finna slide", "meaning": "about to drive over"}], "grammar_notes": ["Zero Copula: The verb 'to be' is omitted. 'He is tweaking' -> 'He tweaking'."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Chief Keef", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "YWyHZNBz6FE", "original_bar": "These b*tches love Sosa, O end or no end. We outside. He tweaking.", "exercise_text": "These girls ______ Sosa, O end or ______ end. We ______. He ______.", "blanks": [{"position": 1, "correct_answers": ["love"], "hint": "adore", "distractor_options": ["hate", "like"]}, {"position": 2, "correct_answers": ["no"], "hint": "negative", "distractor_options": ["know", "go"]}, {"position": 3, "correct_answers": ["outside"], "hint": "outdoors", "distractor_options": ["inside", "away"]}, {"position": 4, "correct_answers": ["tweaking"], "hint": "acting crazy", "distractor_options": ["chilling", "sleeping"]}], "full_translation": "These girls love Sosa, it is O block or nothing. We are outside. He is acting crazy.", "grammar_notes": ["Zero Copula context in typical Chicago drill."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "He is acting crazy. They are outside. You are unprepared.", "expected_drill_output": "He tweaking. They outside. You lackin.", "accepted_variants": ["He tweaking, they outside, you lackin", "He buggin, they outside, you lackin"], "evaluation_rubric": {"zero_copula": {"description": "Omits 'is' and 'are'", "points": 100, "example": "He tweaking"}}, "grammar_explanation": "Drop 'is' and 'are' to form the Zero Copula.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "He tweaking, they outside right now. You lackin'.", "phonetic_tips": ["Drop the 'g' in tweaking and lackin.", "Blend they and outside."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000005"),
        "title": "D5: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 5,
        "audio_url": _jdump({"lesson_title": "D5: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here. I ain't got no money for no games. Don't nobody know nothing.", "formal_translation": "Nobody is doing anything around here. I do not have any money for any games. Nobody knows anything.", "breakdown": [{"abbr": "Ain't nobody doing nothing", "meaning": "Nobody is doing anything"}, {"abbr": "ain't got no", "meaning": "do not have any"}, {"abbr": "Don't nobody know nothing", "meaning": "Nobody knows anything"}], "grammar_notes": ["Negative Concord: Multiple negatives are used to emphasize negation, not cancel it."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games. Ain't nobody sliding today.", "exercise_text": "I ______ got ______ time for ______ games. ______ nobody sliding today.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "do not", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "some"]}, {"position": 3, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "the"]}, {"position": 4, "correct_answers": ["Ain't", "aint"], "hint": "Nobody is", "distractor_options": ["Is", "Not"]}], "full_translation": "I do not have any time for any games. Nobody is driving over today.", "grammar_notes": ["Triple negation: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything. I do not have any money.", "expected_drill_output": "Ain't nobody doing nothing. I ain't got no money.", "accepted_variants": ["Aint nobody doing nothing, I aint got no money"], "evaluation_rubric": {"negative_concord": {"description": "Uses ain't, nobody, and nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Use multiple negatives for emphasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing. I ain't got no money.", "phonetic_tips": ["Stress 'ain't' and 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000006"),
        "title": "D6: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 6,
        "audio_url": _jdump({"lesson_title": "D6: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here. I ain't got no money for no games. Don't nobody know nothing.", "formal_translation": "Nobody is doing anything around here. I do not have any money for any games. Nobody knows anything.", "breakdown": [{"abbr": "Ain't nobody doing nothing", "meaning": "Nobody is doing anything"}, {"abbr": "ain't got no", "meaning": "do not have any"}, {"abbr": "Don't nobody know nothing", "meaning": "Nobody knows anything"}], "grammar_notes": ["Negative Concord: Multiple negatives are used to emphasize negation, not cancel it."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games. Ain't nobody sliding today.", "exercise_text": "I ______ got ______ time for ______ games. ______ nobody sliding today.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "do not", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "some"]}, {"position": 3, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "the"]}, {"position": 4, "correct_answers": ["Ain't", "aint"], "hint": "Nobody is", "distractor_options": ["Is", "Not"]}], "full_translation": "I do not have any time for any games. Nobody is driving over today.", "grammar_notes": ["Triple negation: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything. I do not have any money.", "expected_drill_output": "Ain't nobody doing nothing. I ain't got no money.", "accepted_variants": ["Aint nobody doing nothing, I aint got no money"], "evaluation_rubric": {"negative_concord": {"description": "Uses ain't, nobody, and nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Use multiple negatives for emphasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing. I ain't got no money.", "phonetic_tips": ["Stress 'ain't' and 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000007"),
        "title": "D7: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 7,
        "audio_url": _jdump({"lesson_title": "D7: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here. I ain't got no money for no games. Don't nobody know nothing.", "formal_translation": "Nobody is doing anything around here. I do not have any money for any games. Nobody knows anything.", "breakdown": [{"abbr": "Ain't nobody doing nothing", "meaning": "Nobody is doing anything"}, {"abbr": "ain't got no", "meaning": "do not have any"}, {"abbr": "Don't nobody know nothing", "meaning": "Nobody knows anything"}], "grammar_notes": ["Negative Concord: Multiple negatives are used to emphasize negation, not cancel it."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games. Ain't nobody sliding today.", "exercise_text": "I ______ got ______ time for ______ games. ______ nobody sliding today.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "do not", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "some"]}, {"position": 3, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "the"]}, {"position": 4, "correct_answers": ["Ain't", "aint"], "hint": "Nobody is", "distractor_options": ["Is", "Not"]}], "full_translation": "I do not have any time for any games. Nobody is driving over today.", "grammar_notes": ["Triple negation: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything. I do not have any money.", "expected_drill_output": "Ain't nobody doing nothing. I ain't got no money.", "accepted_variants": ["Aint nobody doing nothing, I aint got no money"], "evaluation_rubric": {"negative_concord": {"description": "Uses ain't, nobody, and nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Use multiple negatives for emphasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing. I ain't got no money.", "phonetic_tips": ["Stress 'ain't' and 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000008"),
        "title": "D8: NYC Hustle (Negative Concord)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 8,
        "audio_url": _jdump({"lesson_title": "D8: NYC Hustle (Negative Concord)", "dialect_focus": "NYC", "modules": {"reading": {"module_type": "reading", "dialect_focus": "NYC", "raw_text": "Ain't nobody doing nothing around here. I ain't got no money for no games. Don't nobody know nothing.", "formal_translation": "Nobody is doing anything around here. I do not have any money for any games. Nobody knows anything.", "breakdown": [{"abbr": "Ain't nobody doing nothing", "meaning": "Nobody is doing anything"}, {"abbr": "ain't got no", "meaning": "do not have any"}, {"abbr": "Don't nobody know nothing", "meaning": "Nobody knows anything"}], "grammar_notes": ["Negative Concord: Multiple negatives are used to emphasize negation, not cancel it."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Pop Smoke", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "oorO2tcOqqU", "original_bar": "I ain't got no time for no games. Ain't nobody sliding today.", "exercise_text": "I ______ got ______ time for ______ games. ______ nobody sliding today.", "blanks": [{"position": 1, "correct_answers": ["ain't"], "hint": "do not", "distractor_options": ["don't", "won't"]}, {"position": 2, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "some"]}, {"position": 3, "correct_answers": ["no"], "hint": "any", "distractor_options": ["any", "the"]}, {"position": 4, "correct_answers": ["Ain't", "aint"], "hint": "Nobody is", "distractor_options": ["Is", "Not"]}], "full_translation": "I do not have any time for any games. Nobody is driving over today.", "grammar_notes": ["Triple negation: ain't, no, no."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Nobody is doing anything. I do not have any money.", "expected_drill_output": "Ain't nobody doing nothing. I ain't got no money.", "accepted_variants": ["Aint nobody doing nothing, I aint got no money"], "evaluation_rubric": {"negative_concord": {"description": "Uses ain't, nobody, and nothing", "points": 100, "example": "Ain't nobody doing nothing"}}, "grammar_explanation": "Use multiple negatives for emphasis.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Ain't nobody doing nothing. I ain't got no money.", "phonetic_tips": ["Stress 'ain't' and 'nothing'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000009"),
        "title": "D9: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 9,
        "audio_url": _jdump({"lesson_title": "D9: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going with that blick? How they getting motion out here?", "formal_translation": "Why did you do that? Where is he going with that gun? How are they gaining momentum out here?", "breakdown": [{"abbr": "Why you do", "meaning": "Why did you do"}, {"abbr": "Where he going", "meaning": "Where is he going"}, {"abbr": "blick", "meaning": "gun"}, {"abbr": "motion", "meaning": "momentum / success"}], "grammar_notes": ["Inverted Syntax: Auxiliary verbs (do, did, are) are omitted in questions. Word order stays the same."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that? Why he capping about his motion?", "exercise_text": "______ you going with that? ______ he capping about his ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Question word", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["Why"], "hint": "Reason", "distractor_options": ["Who", "How"]}, {"position": 3, "correct_answers": ["motion"], "hint": "success", "distractor_options": ["money", "cars"]}], "full_translation": "Where are you going with that? Why is he lying about his success?", "grammar_notes": ["Omits 'are' and 'is' in the questions."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that? Where is he going?", "expected_drill_output": "Why you do that? Where he going?", "accepted_variants": ["Why you do that, where he going", "Why you do that? Where he going with that"], "evaluation_rubric": {"drop_aux": {"description": "Drops 'did' and 'is'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Drop the auxiliary verb to form the question natively.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that? Where he going with that blick?", "phonetic_tips": ["Rise your pitch at the end to indicate a question."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000010"),
        "title": "D10: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 10,
        "audio_url": _jdump({"lesson_title": "D10: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going with that blick? How they getting motion out here?", "formal_translation": "Why did you do that? Where is he going with that gun? How are they gaining momentum out here?", "breakdown": [{"abbr": "Why you do", "meaning": "Why did you do"}, {"abbr": "Where he going", "meaning": "Where is he going"}, {"abbr": "blick", "meaning": "gun"}, {"abbr": "motion", "meaning": "momentum / success"}], "grammar_notes": ["Inverted Syntax: Auxiliary verbs (do, did, are) are omitted in questions. Word order stays the same."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that? Why he capping about his motion?", "exercise_text": "______ you going with that? ______ he capping about his ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Question word", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["Why"], "hint": "Reason", "distractor_options": ["Who", "How"]}, {"position": 3, "correct_answers": ["motion"], "hint": "success", "distractor_options": ["money", "cars"]}], "full_translation": "Where are you going with that? Why is he lying about his success?", "grammar_notes": ["Omits 'are' and 'is' in the questions."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that? Where is he going?", "expected_drill_output": "Why you do that? Where he going?", "accepted_variants": ["Why you do that, where he going", "Why you do that? Where he going with that"], "evaluation_rubric": {"drop_aux": {"description": "Drops 'did' and 'is'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Drop the auxiliary verb to form the question natively.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that? Where he going with that blick?", "phonetic_tips": ["Rise your pitch at the end to indicate a question."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000011"),
        "title": "D11: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 11,
        "audio_url": _jdump({"lesson_title": "D11: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going with that blick? How they getting motion out here?", "formal_translation": "Why did you do that? Where is he going with that gun? How are they gaining momentum out here?", "breakdown": [{"abbr": "Why you do", "meaning": "Why did you do"}, {"abbr": "Where he going", "meaning": "Where is he going"}, {"abbr": "blick", "meaning": "gun"}, {"abbr": "motion", "meaning": "momentum / success"}], "grammar_notes": ["Inverted Syntax: Auxiliary verbs (do, did, are) are omitted in questions. Word order stays the same."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that? Why he capping about his motion?", "exercise_text": "______ you going with that? ______ he capping about his ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Question word", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["Why"], "hint": "Reason", "distractor_options": ["Who", "How"]}, {"position": 3, "correct_answers": ["motion"], "hint": "success", "distractor_options": ["money", "cars"]}], "full_translation": "Where are you going with that? Why is he lying about his success?", "grammar_notes": ["Omits 'are' and 'is' in the questions."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that? Where is he going?", "expected_drill_output": "Why you do that? Where he going?", "accepted_variants": ["Why you do that, where he going", "Why you do that? Where he going with that"], "evaluation_rubric": {"drop_aux": {"description": "Drops 'did' and 'is'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Drop the auxiliary verb to form the question natively.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that? Where he going with that blick?", "phonetic_tips": ["Rise your pitch at the end to indicate a question."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000012"),
        "title": "D12: The Interrogation (Inverted Syntax)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 12,
        "audio_url": _jdump({"lesson_title": "D12: The Interrogation (Inverted Syntax)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "Why you do that? Where he going with that blick? How they getting motion out here?", "formal_translation": "Why did you do that? Where is he going with that gun? How are they gaining momentum out here?", "breakdown": [{"abbr": "Why you do", "meaning": "Why did you do"}, {"abbr": "Where he going", "meaning": "Where is he going"}, {"abbr": "blick", "meaning": "gun"}, {"abbr": "motion", "meaning": "momentum / success"}], "grammar_notes": ["Inverted Syntax: Auxiliary verbs (do, did, are) are omitted in questions. Word order stays the same."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "King Von", "dialect_focus": "Chicago", "audio_s3_url": "dummy", "youtube_video_id": "g0v7Ow6Epog", "original_bar": "Where you going with that? Why he capping about his motion?", "exercise_text": "______ you going with that? ______ he capping about his ______?", "blanks": [{"position": 1, "correct_answers": ["Where"], "hint": "Question word", "distractor_options": ["Why", "How"]}, {"position": 2, "correct_answers": ["Why"], "hint": "Reason", "distractor_options": ["Who", "How"]}, {"position": 3, "correct_answers": ["motion"], "hint": "success", "distractor_options": ["money", "cars"]}], "full_translation": "Where are you going with that? Why is he lying about his success?", "grammar_notes": ["Omits 'are' and 'is' in the questions."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "Why did you do that? Where is he going?", "expected_drill_output": "Why you do that? Where he going?", "accepted_variants": ["Why you do that, where he going", "Why you do that? Where he going with that"], "evaluation_rubric": {"drop_aux": {"description": "Drops 'did' and 'is'", "points": 100, "example": "Why you do that?"}}, "grammar_explanation": "Drop the auxiliary verb to form the question natively.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "Why you do that? Where he going with that blick?", "phonetic_tips": ["Rise your pitch at the end to indicate a question."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000013"),
        "title": "D13: Territory (Possessives)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 13,
        "audio_url": _jdump({"lesson_title": "D13: Territory (Possessives)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "They outside they house. We taking they spot. They lost they motion completely.", "formal_translation": "They are outside their house. We are taking their spot. They lost their momentum completely.", "breakdown": [{"abbr": "they house", "meaning": "their house"}, {"abbr": "they spot", "meaning": "their spot"}, {"abbr": "they motion", "meaning": "their momentum"}], "grammar_notes": ["Possessive Substitution: 'They' is used instead of 'their' for possession."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Kay Flock", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "gGJS8W9emac", "original_bar": "They all in they feelings. They lost they motion.", "exercise_text": "They all in ______ feelings. They lost ______ ______.", "blanks": [{"position": 1, "correct_answers": ["they"], "hint": "their", "distractor_options": ["their", "there"]}, {"position": 2, "correct_answers": ["they"], "hint": "their", "distractor_options": ["their", "the"]}, {"position": 3, "correct_answers": ["motion"], "hint": "momentum", "distractor_options": ["money", "spot"]}], "full_translation": "They are all in their feelings. They lost their momentum.", "grammar_notes": ["'they feelings' instead of 'their feelings'."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "They are outside their house. They lost their momentum.", "expected_drill_output": "They outside they house. They lost they motion.", "accepted_variants": ["They outside they house, they lost they motion"], "evaluation_rubric": {"possessive": {"description": "Uses 'they' instead of 'their'", "points": 100, "example": "they house"}}, "grammar_explanation": "Replace 'their' with 'they'.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "They outside they house. They lost they motion.", "phonetic_tips": ["Blend 'they' and 'outside'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000014"),
        "title": "D14: Territory (Possessives)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 14,
        "audio_url": _jdump({"lesson_title": "D14: Territory (Possessives)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "They outside they house. We taking they spot. They lost they motion completely.", "formal_translation": "They are outside their house. We are taking their spot. They lost their momentum completely.", "breakdown": [{"abbr": "they house", "meaning": "their house"}, {"abbr": "they spot", "meaning": "their spot"}, {"abbr": "they motion", "meaning": "their momentum"}], "grammar_notes": ["Possessive Substitution: 'They' is used instead of 'their' for possession."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Kay Flock", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "gGJS8W9emac", "original_bar": "They all in they feelings. They lost they motion.", "exercise_text": "They all in ______ feelings. They lost ______ ______.", "blanks": [{"position": 1, "correct_answers": ["they"], "hint": "their", "distractor_options": ["their", "there"]}, {"position": 2, "correct_answers": ["they"], "hint": "their", "distractor_options": ["their", "the"]}, {"position": 3, "correct_answers": ["motion"], "hint": "momentum", "distractor_options": ["money", "spot"]}], "full_translation": "They are all in their feelings. They lost their momentum.", "grammar_notes": ["'they feelings' instead of 'their feelings'."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "They are outside their house. They lost their momentum.", "expected_drill_output": "They outside they house. They lost they motion.", "accepted_variants": ["They outside they house, they lost they motion"], "evaluation_rubric": {"possessive": {"description": "Uses 'they' instead of 'their'", "points": 100, "example": "they house"}}, "grammar_explanation": "Replace 'their' with 'they'.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "They outside they house. They lost they motion.", "phonetic_tips": ["Blend 'they' and 'outside'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
    },
    {
        "id": uuid.UUID("55555555-0000-0000-0000-000000000015"),
        "title": "D15: Territory (Possessives)",
        "dialect_segment": "midwest",
        "level_band": "B1",
        "day_order": 15,
        "audio_url": _jdump({"lesson_title": "D15: Territory (Possessives)", "dialect_focus": "General", "modules": {"reading": {"module_type": "reading", "dialect_focus": "General", "raw_text": "They outside they house. We taking they spot. They lost they motion completely.", "formal_translation": "They are outside their house. We are taking their spot. They lost their momentum completely.", "breakdown": [{"abbr": "they house", "meaning": "their house"}, {"abbr": "they spot", "meaning": "their spot"}, {"abbr": "they motion", "meaning": "their momentum"}], "grammar_notes": ["Possessive Substitution: 'They' is used instead of 'their' for possession."], "cefr_target": "B1.1", "xp_reward": 10}, "listening": {"module_type": "listening", "artist": "Kay Flock", "dialect_focus": "NYC", "audio_s3_url": "dummy", "youtube_video_id": "gGJS8W9emac", "original_bar": "They all in they feelings. They lost they motion.", "exercise_text": "They all in ______ feelings. They lost ______ ______.", "blanks": [{"position": 1, "correct_answers": ["they"], "hint": "their", "distractor_options": ["their", "there"]}, {"position": 2, "correct_answers": ["they"], "hint": "their", "distractor_options": ["their", "the"]}, {"position": 3, "correct_answers": ["motion"], "hint": "momentum", "distractor_options": ["money", "spot"]}], "full_translation": "They are all in their feelings. They lost their momentum.", "grammar_notes": ["'they feelings' instead of 'their feelings'."], "cefr_target": "B1.1", "xp_reward": 15}, "writing": {"module_type": "writing", "formal_input": "They are outside their house. They lost their momentum.", "expected_drill_output": "They outside they house. They lost they motion.", "accepted_variants": ["They outside they house, they lost they motion"], "evaluation_rubric": {"possessive": {"description": "Uses 'they' instead of 'their'", "points": 100, "example": "they house"}}, "grammar_explanation": "Replace 'their' with 'they'.", "cefr_target": "B1.1", "xp_reward": 20}, "speaking": {"module_type": "speaking", "target_phrase": "They outside they house. They lost they motion.", "phonetic_tips": ["Blend 'they' and 'outside'."], "cefr_target": "B1.1", "xp_reward": 25}}}),
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
