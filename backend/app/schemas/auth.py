import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    username: str
    token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    level_band: str
    xp_total: int
    created_at: datetime

    model_config = {"from_attributes": True}
