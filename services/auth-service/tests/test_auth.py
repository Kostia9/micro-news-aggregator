import asyncio

import pytest
from app.models.user import User
from app.routes.auth import login, logout, register
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.jwt import create_access_token, decode_token
from app.services.password import hash_password, verify_password
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.exc import IntegrityError


class FakeSession:
    def __init__(self, existing_user=None, raise_on_commit: bool = False) -> None:
        self.existing_user = existing_user
        self.raise_on_commit = raise_on_commit
        self.added = []
        self.committed = False
        self.rolled_back = False

    async def scalar(self, stmt):
        return self.existing_user

    def add(self, obj) -> None:
        self.added.append(obj)

    async def commit(self) -> None:
        if self.raise_on_commit:
            raise IntegrityError(None, None, Exception("unique"))
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True

    async def refresh(self, obj) -> None:
        obj.id = 42


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}
        self.ttls: dict[str, int | None] = {}
        self.deleted: list[str] = []

    async def set(self, key: str, value: str, ex=None) -> None:
        self.store[key] = value
        self.ttls[key] = ex

    async def delete(self, key: str) -> None:
        self.deleted.append(key)


_HASHED_SECRET = hash_password("secret123")


def _user(email: str = "user@example.com") -> User:
    user = User(
        email=email,
        hashed_password=_HASHED_SECRET,
        topics=["technology"],
    )
    user.id = 7
    return user


def test_register_success() -> None:
    session = FakeSession()
    redis = FakeRedis()
    payload = RegisterRequest(
        email="new@example.com",
        password="secret123",
        topics=["technology"],
    )

    response = asyncio.run(register(payload, session=session, redis=redis))

    assert response.access_token
    assert response.expires_in > 0
    assert session.committed is True
    assert len(session.added) == 1
    assert len(redis.store) == 1
    key = next(iter(redis.store))
    assert key.startswith("jwt:allow:")
    assert redis.ttls[key] == response.expires_in


def test_register_duplicate_email_returns_409() -> None:
    session = FakeSession(existing_user=_user())

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            register(
                RegisterRequest(email="user@example.com", password="secret123"),
                session=session,
                redis=FakeRedis(),
            )
        )

    assert exc.value.status_code == 409


def test_register_integrity_error_rolls_back_and_returns_409() -> None:
    session = FakeSession(raise_on_commit=True)
    redis = FakeRedis()

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            register(
                RegisterRequest(email="new@example.com", password="secret123"),
                session=session,
                redis=redis,
            )
        )

    assert exc.value.status_code == 409
    assert session.rolled_back is True
    assert redis.store == {}


def test_login_success() -> None:
    redis = FakeRedis()

    response = asyncio.run(
        login(
            LoginRequest(email="user@example.com", password="secret123"),
            session=FakeSession(existing_user=_user()),
            redis=redis,
        )
    )

    assert response.access_token
    assert len(redis.store) == 1


def test_login_wrong_password_returns_401() -> None:
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            login(
                LoginRequest(email="user@example.com", password="wrongpass"),
                session=FakeSession(existing_user=_user()),
                redis=FakeRedis(),
            )
        )

    assert exc.value.status_code == 401


def test_login_unknown_email_returns_401() -> None:
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            login(
                LoginRequest(email="missing@example.com", password="secret123"),
                session=FakeSession(),
                redis=FakeRedis(),
            )
        )

    assert exc.value.status_code == 401


def test_logout_deletes_allowlisted_jti() -> None:
    redis = FakeRedis()
    issued = create_access_token(user_id=7)

    asyncio.run(
        logout(
            HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=issued.token,
            ),
            redis=redis,
        )
    )

    assert redis.deleted == [f"jwt:allow:{issued.jti}"]


def test_logout_invalid_token_returns_401() -> None:
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            logout(
                HTTPAuthorizationCredentials(scheme="Bearer", credentials="garbage"),
                redis=FakeRedis(),
            )
        )

    assert exc.value.status_code == 401


def test_jwt_roundtrip_contains_subject_and_jti() -> None:
    issued = create_access_token(user_id=99)
    payload = decode_token(issued.token)

    assert payload["sub"] == "99"
    assert payload["jti"] == issued.jti
    assert payload["iat"] < payload["exp"]


def test_decode_invalid_token_raises_jwt_error() -> None:
    with pytest.raises(JWTError):
        decode_token("garbage")


def test_hash_password_verification() -> None:
    hashed = hash_password("secret123")

    assert verify_password("secret123", hashed) is True
    assert verify_password("wrongpass", hashed) is False
