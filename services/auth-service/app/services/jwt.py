import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import settings


@dataclass(frozen=True)
class IssuedToken:
    token: str
    jti: str
    ttl_seconds: int


def create_access_token(user_id: int) -> IssuedToken:
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    ttl = settings.access_token_ttl_seconds
    payload = {
        "sub": str(user_id),
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl)).timestamp()),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return IssuedToken(token=token, jti=jti, ttl_seconds=ttl)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
