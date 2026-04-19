import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_session
from app.db.redis import get_redis
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.jwt import create_access_token, decode_token
from app.services.password import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=True)

ALLOWLIST_KEY = "jwt:allow:{jti}"


async def _issue_token(user_id: int, redis: aioredis.Redis) -> TokenResponse:
    issued = create_access_token(user_id)
    await redis.set(
        ALLOWLIST_KEY.format(jti=issued.jti), str(user_id), ex=issued.ttl_seconds
    )
    return TokenResponse(access_token=issued.token, expires_in=issued.ttl_seconds)


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_session),
    redis: aioredis.Redis = Depends(get_redis),
) -> TokenResponse:
    existing = await session.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email already registered"
        )
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        topics=payload.topics,
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email already registered"
        ) from exc
    await session.refresh(user)
    return await _issue_token(user.id, redis)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
    redis: aioredis.Redis = Depends(get_redis),
) -> TokenResponse:
    user = await session.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )
    return await _issue_token(user.id, redis)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    redis: aioredis.Redis = Depends(get_redis),
) -> None:
    try:
        payload = decode_token(credentials.credentials)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        ) from exc
    jti = payload.get("jti")
    if jti:
        await redis.delete(ALLOWLIST_KEY.format(jti=jti))
