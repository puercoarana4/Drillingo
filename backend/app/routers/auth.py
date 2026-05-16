from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Dependency that validates the JWT and returns the current User."""
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
        )
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.
    - Returns 409 if email is already registered.
    - Returns 422 if password is shorter than 8 characters.
    """
    service = AuthService(db)
    return await service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and obtain JWT",
)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate with email and password.
    - Returns 401 if credentials are invalid.
    """
    service = AuthService(db)
    return await service.login(data)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def me(current_user=Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user
