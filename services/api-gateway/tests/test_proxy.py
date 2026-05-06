import asyncio
from types import SimpleNamespace

import pytest
from app.config import settings
from app.routes.proxy import authorize_feed_request, proxy_auth
from fastapi import HTTPException
from jose import jwt


class FakeRedis:
    def __init__(self, value: str | None) -> None:
        self.value = value

    async def get(self, key: str) -> str | None:
        return self.value


class FakeUpstreamResponse:
    status_code = 201
    content = b'{"ok": true}'
    headers = {"content-type": "application/json"}


class FakeHttpClient:
    def __init__(self) -> None:
        self.calls = []

    async def request(self, method: str, url: str, **kwargs):
        self.calls.append((method, url, kwargs))
        return FakeUpstreamResponse()


class FakeRequest:
    method = "POST"
    headers = {"content-type": "application/json"}
    url = SimpleNamespace(query="")

    def __init__(self, client: FakeHttpClient) -> None:
        self.app = SimpleNamespace(state=SimpleNamespace(http_client=client))

    async def body(self) -> bytes:
        return b'{"email": "user@example.com"}'


def test_auth_proxy_forwards_without_gateway_jwt() -> None:
    client = FakeHttpClient()
    response = asyncio.run(proxy_auth("login", FakeRequest(client)))

    assert response.status_code == 201
    assert client.calls[0][0] == "POST"
    assert client.calls[0][1] == "http://auth-lb/auth/login"


def test_feed_auth_rejects_missing_token() -> None:
    with pytest.raises(HTTPException) as exc:
        asyncio.run(authorize_feed_request(None, FakeRedis("1")))

    assert exc.value.status_code == 401


def test_feed_auth_rejects_invalid_token() -> None:
    with pytest.raises(HTTPException) as exc:
        asyncio.run(authorize_feed_request("Bearer invalid", FakeRedis("1")))

    assert exc.value.status_code == 401


def test_feed_auth_accepts_allowlisted_jwt() -> None:
    token = jwt.encode(
        {"sub": "1", "jti": "token-id"},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    payload = asyncio.run(authorize_feed_request(f"Bearer {token}", FakeRedis("1")))

    assert payload["sub"] == "1"
    assert payload["jti"] == "token-id"


def test_feed_auth_rejects_revoked_jwt() -> None:
    token = jwt.encode(
        {"sub": "1", "jti": "token-id"},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(authorize_feed_request(f"Bearer {token}", FakeRedis(None)))

    assert exc.value.status_code == 401
