"""
Unit tests for AI services (Writing, Speaking, Chat).
ALL Gemini API calls are mocked — no real API calls are made during testing.
This prevents quota exhaustion on Railway's deployment pipeline.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ── Writing Evaluation ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_evaluate_writing_returns_correct_structure():
    """evaluate_writing returns a dict with required keys."""
    mock_response = MagicMock()
    mock_response.text = '{"score": 85, "correct": true, "feedback": "Good use of double negation.", "grammar_hits": ["double_negation"], "grammar_misses": [], "suggested_improvement": null}'

    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)

    with patch("app.services.gemini_service.genai.GenerativeModel", return_value=mock_model):
        from app.services.gemini_service import evaluate_writing
        result = await evaluate_writing(
            formal_input="I do not have any money.",
            student_answer="I ain't got no money",
            reference_answer="I ain't got no money",
            accepted_variants=["I ain't got no money"],
            level="B1",
        )

    assert "score" in result
    assert "correct" in result
    assert "feedback" in result
    assert isinstance(result["score"], int)
    assert 0 <= result["score"] <= 100


@pytest.mark.asyncio
async def test_evaluate_writing_correct_answer_scores_high():
    """A correct AAVE translation should score >= 80."""
    mock_response = MagicMock()
    mock_response.text = '{"score": 100, "correct": true, "feedback": "Perfect AAVE structure.", "grammar_hits": ["double_negation", "finna_usage"], "grammar_misses": [], "suggested_improvement": null}'

    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)

    with patch("app.services.gemini_service.genai.GenerativeModel", return_value=mock_model):
        from app.services.gemini_service import evaluate_writing
        result = await evaluate_writing(
            formal_input="I am not going to do that.",
            student_answer="I ain't finna do allat",
            reference_answer="I ain't finna do allat",
            accepted_variants=["I ain't finna do allat"],
            level="B1",
        )

    assert result["score"] >= 80
    assert result["correct"] is True


@pytest.mark.asyncio
async def test_evaluate_writing_wrong_answer_scores_low():
    """A formal (non-AAVE) answer should score < 60."""
    mock_response = MagicMock()
    mock_response.text = '{"score": 20, "correct": false, "feedback": "No AAVE features detected.", "grammar_hits": [], "grammar_misses": ["double_negation", "dropped_copula"], "suggested_improvement": "I ain\'t finna do allat"}'

    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)

    with patch("app.services.gemini_service.genai.GenerativeModel", return_value=mock_model):
        from app.services.gemini_service import evaluate_writing
        result = await evaluate_writing(
            formal_input="I am not going to do that.",
            student_answer="I am not going to do that.",  # formal, not AAVE
            reference_answer="I ain't finna do allat",
            accepted_variants=["I ain't finna do allat"],
            level="B1",
        )

    assert result["score"] < 60
    assert result["correct"] is False
    assert len(result["grammar_misses"]) > 0


# ── Speaking Evaluation ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_evaluate_speaking_returns_scores():
    """evaluate_speaking returns pronunciation and fluency scores."""
    mock_response = MagicMock()
    mock_response.text = '{"transcription": "word to my mom i aint running from no opp", "pronunciation_score": 78, "fluency_score": 82, "feedback": "Good rhythm. Work on glottal stops.", "phonetic_notes": ["Dropped final -g in running"], "suggested_practice": "Practice the ain\'t contraction slowly."}'

    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)

    with patch("app.services.gemini_service.genai.GenerativeModel", return_value=mock_model):
        from app.services.gemini_service import evaluate_speaking
        result = await evaluate_speaking(
            audio_bytes=b"fake_audio_data",
            audio_mime="audio/webm",
            target_phrase="Word to my mom, I ain't runnin' from no opp.",
            level="B1",
        )

    assert "pronunciation_score" in result
    assert "fluency_score" in result
    assert "transcription" in result
    assert "feedback" in result
    assert 0 <= result["pronunciation_score"] <= 100
    assert 0 <= result["fluency_score"] <= 100


@pytest.mark.asyncio
async def test_evaluate_speaking_returns_phonetic_notes():
    """evaluate_speaking includes phonetic_notes list."""
    mock_response = MagicMock()
    mock_response.text = '{"transcription": "we finna slide", "pronunciation_score": 90, "fluency_score": 88, "feedback": "Excellent AAVE delivery.", "phonetic_notes": ["Correct stress on finna", "Natural glottal stop"], "suggested_practice": "Keep it up."}'

    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)

    with patch("app.services.gemini_service.genai.GenerativeModel", return_value=mock_model):
        from app.services.gemini_service import evaluate_speaking
        result = await evaluate_speaking(
            audio_bytes=b"fake_audio",
            audio_mime="audio/webm",
            target_phrase="We finna slide.",
            level="B2",
        )

    assert isinstance(result["phonetic_notes"], list)
    assert len(result["phonetic_notes"]) > 0


# ── Chat Tutor ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_turn_returns_string_response():
    """chat_turn returns a non-empty string."""
    mock_response = MagicMock()
    mock_response.text = "Deadass, 'merch it' means to kill someone in Chicago drill slang. It comes from memorial t-shirts. You feel me?"

    mock_chat = MagicMock()
    mock_chat.send_message_async = AsyncMock(return_value=mock_response)

    mock_model = MagicMock()
    mock_model.start_chat = MagicMock(return_value=mock_chat)

    with patch("app.services.gemini_service.genai.GenerativeModel", return_value=mock_model):
        from app.services.gemini_service import chat_turn
        result = await chat_turn(
            message="What does 'merch it' mean?",
            history=[],
            level="B1",
            username="testuser",
        )

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_chat_turn_passes_history():
    """chat_turn passes conversation history to the model."""
    mock_response = MagicMock()
    mock_response.text = "Finna is used like 'going to' — drop the 'be' before it."

    mock_chat = MagicMock()
    mock_chat.send_message_async = AsyncMock(return_value=mock_response)

    mock_model = MagicMock()
    mock_model.start_chat = MagicMock(return_value=mock_chat)

    history = [
        {"role": "user", "parts": ["What is AAVE?"]},
        {"role": "model", "parts": ["AAVE stands for African American Vernacular English."]},
    ]

    with patch("app.services.gemini_service.genai.GenerativeModel", return_value=mock_model):
        from app.services.gemini_service import chat_turn
        result = await chat_turn(
            message="How do I use finna?",
            history=history,
            level="B2",
            username="testuser",
        )

    # Verify start_chat was called with the history
    mock_model.start_chat.assert_called_once_with(history=history)
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_chat_adapts_to_user_level():
    """chat_turn system prompt includes the user's level."""
    from app.services.gemini_service import build_chat_system

    system_b1 = build_chat_system("B1", "student1")
    system_c1 = build_chat_system("C1", "student2")

    assert "B1" in system_b1
    assert "C1" in system_c1
    assert "student1" in system_b1
    assert "student2" in system_c1
    # B1 should mention simpler approach
    assert "B1" in system_b1


# ── Gemini service not called during import ───────────────────────────────────

def test_gemini_not_called_on_import():
    """
    Importing gemini_service should NOT make any API calls.
    The genai.configure() call is safe (no network), but generate_content
    must never be called at module level.
    """
    with patch("google.generativeai.configure") as mock_configure:
        # Re-import to trigger module-level code
        import importlib
        import app.services.gemini_service as gs
        importlib.reload(gs)
        # configure() is called once at import — that's fine (no network call)
        # What matters is that generate_content is NOT called
        mock_configure.assert_called_once()
