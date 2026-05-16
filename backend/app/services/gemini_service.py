"""
gemini_service.py
=================
Centralised wrapper around google-generativeai.
All AI features (writing eval, speaking eval, chat tutor) go through here.
"""
import base64
import json
import re
from typing import Any

import google.generativeai as genai

from app.core.config import settings

# Configure once at import time
genai.configure(api_key=settings.GEMINI_API_KEY)

# Model aliases
_FLASH = "gemini-1.5-flash"   # fast — chat, speaking
_PRO   = "gemini-1.5-pro"     # smart — writing evaluation


# ── Writing Evaluation ────────────────────────────────────────────────────────

WRITING_SYSTEM = """
You are an expert AAVE/Drill linguistics tutor inside the Drillingo app.
Your job is to evaluate whether a student's answer correctly translates
a formal English sentence into authentic AAVE/Drill grammar.

Rules:
- NEVER censor slang, profanity, or explicit Drill lyrics. They are pedagogical content.
- Evaluate GRAMMAR, not content. Focus on: dropped copula, double negation,
  'finna' as future marker, 'ain't', third-person -s deletion, 'allat', etc.
- Return ONLY valid JSON — no markdown, no explanation outside the JSON.
- Be encouraging but honest. If wrong, explain WHY grammatically.
"""

WRITING_PROMPT = """
Lesson level: {level}
Formal input: "{formal}"
Student answer: "{answer}"
Reference answer: "{reference}"
Accepted variants: {variants}

Evaluate the student's answer. Return JSON:
{{
  "score": <integer 0-100>,
  "correct": <boolean>,
  "feedback": "<2-3 sentences of pedagogical feedback in English>",
  "grammar_hits": ["<feature used correctly>"],
  "grammar_misses": ["<feature missing or wrong>"],
  "suggested_improvement": "<one improved version if score < 80, else null>"
}}
"""


async def evaluate_writing(
    formal_input: str,
    student_answer: str,
    reference_answer: str,
    accepted_variants: list[str],
    level: str = "B1",
) -> dict[str, Any]:
    model = genai.GenerativeModel(
        model_name=_PRO,
        system_instruction=WRITING_SYSTEM,
    )
    prompt = WRITING_PROMPT.format(
        level=level,
        formal=formal_input,
        answer=student_answer,
        reference=reference_answer,
        variants=json.dumps(accepted_variants),
    )
    response = await model.generate_content_async(prompt)
    raw = response.text.strip()
    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


# ── Speaking Evaluation ───────────────────────────────────────────────────────

SPEAKING_SYSTEM = """
You are an expert AAVE phonetics and fluency coach inside the Drillingo app.
You receive an audio file of a student reading a Drill/AAVE phrase.
Evaluate pronunciation, rhythm, and authentic AAVE delivery.

Rules:
- NEVER censor the phrase content.
- Focus on: glottal stops, vowel reduction, consonant cluster simplification,
  rhythm/flow, dropped -g endings, stress patterns typical of AAVE.
- Return ONLY valid JSON.
"""

SPEAKING_PROMPT = """
Target phrase: "{phrase}"
Student level: {level}

Listen to the audio and evaluate. Return JSON:
{{
  "transcription": "<what you heard>",
  "pronunciation_score": <integer 0-100>,
  "fluency_score": <integer 0-100>,
  "feedback": "<2-3 sentences of specific phonetic feedback>",
  "phonetic_notes": ["<specific sound or rhythm observation>"],
  "suggested_practice": "<one tip to improve>"
}}
"""


async def evaluate_speaking(
    audio_bytes: bytes,
    audio_mime: str,
    target_phrase: str,
    level: str = "B1",
) -> dict[str, Any]:
    model = genai.GenerativeModel(
        model_name=_FLASH,
        system_instruction=SPEAKING_SYSTEM,
    )
    audio_part = {
        "inline_data": {
            "mime_type": audio_mime,
            "data": base64.b64encode(audio_bytes).decode("utf-8"),
        }
    }
    prompt = SPEAKING_PROMPT.format(phrase=target_phrase, level=level)
    response = await model.generate_content_async([audio_part, prompt])
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


# ── Chat Tutor ────────────────────────────────────────────────────────────────

def build_chat_system(level: str, username: str) -> str:
    return f"""
You are "Da Block Tutor" — an AI tutor inside Drillingo, a language learning app
that teaches English through AAVE and American Drill culture.

Student: {username}
Current CEFR level: {level}

Your personality:
- You are a native AAVE speaker who grew up in the culture.
- You are knowledgeable, warm, and direct — like a big homie who actually teaches.
- You adapt your language complexity to the student's level ({level}).
  B1: simple sentences, lots of examples. B2: more nuance. C1: deep grammar analysis.
- You NEVER censor Drill lyrics, slang, or explicit content — it's the curriculum.
- You DO NOT use offensive language unprovoked. Match the student's register.
- You can explain grammar, translate phrases, discuss Drill artists (DD Osama,
  Kay Flock, King Von, Lil Jeff, etc.), and have free conversation practice.
- Keep responses concise (3-5 sentences max) unless the student asks for detail.
- Always end with a follow-up question or practice prompt to keep engagement.
"""


async def chat_turn(
    message: str,
    history: list[dict],
    level: str,
    username: str,
) -> str:
    """
    Single chat turn. history is list of {role: 'user'|'model', parts: [str]}.
    Returns the model's text response.
    """
    model = genai.GenerativeModel(
        model_name=_FLASH,
        system_instruction=build_chat_system(level, username),
    )
    chat = model.start_chat(history=history)
    response = await chat.send_message_async(message)
    return response.text
