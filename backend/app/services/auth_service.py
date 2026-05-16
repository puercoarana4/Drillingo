from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, data: RegisterRequest) -> TokenResponse:
        """
        Register a new user.
        Raises 409 if email already exists.
        Password length is validated by the Pydantic schema (min 8 chars → 422).
        """
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        hashed = hash_password(data.password)
        user = await self.repo.create(
            email=data.email,
            username=data.username,
            password_hash=hashed,
        )

        token = create_access_token({"sub": str(user.id), "email": user.email})
        return TokenResponse(
            user_id=user.id,
            email=user.email,
            username=user.username,
            token=token,
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        """
        Authenticate a user.
        Raises 401 if email not found or password is incorrect.
        """
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        token = create_access_token({"sub": str(user.id), "email": user.email})
        return TokenResponse(
            user_id=user.id,
            email=user.email,
            username=user.username,
            token=token,
        )
