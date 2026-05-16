"""
Unit tests for the Auth module.
Tests use TestClient with mocked DB dependencies to avoid requiring a live database.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── Health check ─────────────────────────────────────────────────────────────

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── Schema validation (no DB needed) ─────────────────────────────────────────

def test_register_password_too_short_returns_422():
    """Req 1.4: password shorter than 8 chars → Pydantic raises 422."""
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "short"},
    )
    assert response.status_code == 422
    body = response.json()
    assert any(
        "8 characters" in str(err.get("msg", "")) or "password" in str(err).lower()
        for err in body.get("detail", [])
    )


def test_register_invalid_email_returns_422():
    """Invalid email format → 422."""
    response = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "username": "testuser", "password": "validpass123"},
    )
    assert response.status_code == 422


# ── Security utilities (pure functions, no DB) ────────────────────────────────

def test_hash_password_is_not_plaintext():
    """Req 1.7: bcrypt hash must differ from plain text."""
    from app.core.security import hash_password

    plain = "mysecretpassword"
    hashed = hash_password(plain)
    assert hashed != plain
    assert hashed.startswith("$2b$")  # bcrypt prefix


def test_verify_password_correct():
    """Req 1.7: verify_password returns True for matching password."""
    from app.core.security import hash_password, verify_password

    plain = "mysecretpassword"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_password_wrong():
    """verify_password returns False for wrong password."""
    from app.core.security import hash_password, verify_password

    hashed = hash_password("correctpassword")
    assert verify_password("wrongpassword", hashed) is False


def test_jwt_round_trip():
    """JWT create → decode round-trip preserves payload."""
    from app.core.security import create_access_token, decode_token

    data = {"sub": "user-uuid-123", "email": "test@example.com"}
    token = create_access_token(data)
    assert isinstance(token, str)

    decoded = decode_token(token)
    assert decoded["sub"] == "user-uuid-123"
    assert decoded["email"] == "test@example.com"


def test_decode_invalid_token_raises_401():
    """decode_token raises HTTPException 401 for garbage token."""
    from fastapi import HTTPException
    from app.core.security import decode_token

    with pytest.raises(HTTPException) as exc_info:
        decode_token("this.is.not.a.valid.jwt")
    assert exc_info.value.status_code == 401
    assert "Token expired or invalid" in exc_info.value.detail


# ── Service layer (mocked repository) ────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_duplicate_email_raises_409():
    """Req 1.3: duplicate email → AuthService raises 409."""
    from fastapi import HTTPException
    from app.services.auth_service import AuthService
    from app.schemas.auth import RegisterRequest

    mock_db = AsyncMock()
    service = AuthService(mock_db)

    # Simulate existing user returned by repo
    existing_user = MagicMock()
    with patch.object(service.repo, "get_by_email", return_value=existing_user):
        with pytest.raises(HTTPException) as exc_info:
            await service.register(
                RegisterRequest(
                    email="dup@example.com",
                    username="dupuser",
                    password="validpass123",
                )
            )
    assert exc_info.value.status_code == 409
    assert "Email already registered" in exc_info.value.detail


@pytest.mark.asyncio
async def test_login_invalid_credentials_raises_401():
    """Req 1.6: wrong password → AuthService raises 401."""
    from fastapi import HTTPException
    from app.services.auth_service import AuthService
    from app.schemas.auth import LoginRequest

    mock_db = AsyncMock()
    service = AuthService(mock_db)

    # Simulate user not found
    with patch.object(service.repo, "get_by_email", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await service.login(
                LoginRequest(email="nobody@example.com", password="somepassword")
            )
    assert exc_info.value.status_code == 401
    assert "Invalid credentials" in exc_info.value.detail
