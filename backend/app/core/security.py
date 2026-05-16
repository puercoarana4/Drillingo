from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(plain: str) -> str:
    """Hash a plain-text password using bcrypt (cost factor 12)."""
    password_bytes = plain.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict[str, Any]) -> str:
    """Create a JWT access token with 24-hour expiry."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token. Raises 401 if invalid or expired."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
