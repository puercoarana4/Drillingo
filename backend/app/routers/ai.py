"""
ai.py — AI-powered endpoints: writing eval, speaking eval, chat tutor.
All three use Gemini via gemini_service.py.
"""
import json
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.services.gemini_service import chat_turn, evaluate_speaking, evaluate_writing

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class WritingEvalRequest(BaseModel):
    formal_input: str
    student_answer: str
    reference_answer: str
    accepted_variants: list[str] = []
    level: str = "B1"


class WritingEvalResponse(BaseModel):
    score: int
    correct: bool
    feedback: str
    grammar_hits: list[str] = []
    grammar_misses: list[str] = []
    suggested_improvement: str | None = None


class ChatMessage(BaseModel):
    role: str   # "user" | "model"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str


# ── Writing Evaluation ────────────────────────────────────────────────────────

@router.post(
    "/writing/evaluate",
    response_model=WritingEvalResponse,
    summary="Evaluate a student's Drill/AAVE translation using Gemini",
)
async def writing_evaluate(
    data: WritingEvalRequest,
    current_user=Depends(get_current_user),
):
    """
    Gemini evaluates whether the student's answer correctly uses AAVE grammar.
    Returns score (0-100), feedback, grammar hits/misses, and improvement suggestion.
    """
    try:
        result = await evaluate_writing(
            formal_input=data.formal_input,
            student_answer=data.student_answer,
            reference_answer=data.reference_answer,
            accepted_variants=data.accepted_variants,
            level=getattr(current_user, "level_band", "B1"),
        )
        return WritingEvalResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini evaluation failed: {str(exc)}",
        )


# ── Speaking Evaluation ───────────────────────────────────────────────────────

@router.post(
    "/speaking/evaluate",
    summary="Evaluate spoken AAVE pronunciation using Gemini Audio",
)
async def speaking_evaluate(
    target_phrase: str = Form(...),
    level: str = Form("B1"),
    audio: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """
    Accepts audio file (webm/ogg/mp4) + target phrase.
    Gemini 1.5 Flash processes audio natively — no separate STT step.
    Returns pronunciation_score, fluency_score, feedback, phonetic_notes.
    """
    audio_bytes = await audio.read()
    mime = audio.content_type or "audio/webm"

    try:
        result = await evaluate_speaking(
            audio_bytes=audio_bytes,
            audio_mime=mime,
            target_phrase=target_phrase,
            level=level,
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini speaking evaluation failed: {str(exc)}",
        )


# ── Chat Tutor (SSE streaming) ────────────────────────────────────────────────

@router.post(
    "/chat",
    summary="Da Block Tutor — AI chat with SSE streaming",
)
async def chat(
    data: ChatRequest,
    current_user=Depends(get_current_user),
):
    """
    Streams Gemini response as Server-Sent Events.
    Frontend reads the stream and appends tokens as they arrive.
    History is maintained client-side and sent with each request.
    """
    level = getattr(current_user, "level_band", "B1")
    username = getattr(current_user, "username", "student")

    # Convert history to Gemini format
    gemini_history = [
        {"role": msg.role, "parts": [msg.content]}
        for msg in data.history
    ]

    async def event_stream():
        try:
            reply = await chat_turn(
                message=data.message,
                history=gemini_history,
                level=level,
                username=username,
            )
            # Stream word by word for perceived speed
            words = reply.split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'token': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True, 'full': reply})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
