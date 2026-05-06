from collections.abc import Mapping

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, HTTPException, Request, Response, status
from jose import JWTError, jwt

from app.config import settings

router = APIRouter()

ALLOWLIST_KEY = "jwt:allow:{jti}"
HOP_BY_HOP_HEADERS = {
    "connection",
    "content-encoding",
    "content-length",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


def _headers_for_upstream(headers: Mapping[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() != "host"
    }


def _headers_for_downstream(headers: Mapping[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }


async def _forward(
    client: httpx.AsyncClient,
    request: Request,
    base_url: str,
    path: str,
) -> Response:
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    upstream = await client.request(
        request.method,
        url,
        headers=_headers_for_upstream(request.headers),
        content=await request.body(),
    )
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=_headers_for_downstream(upstream.headers),
    )


async def authorize_feed_request(
    authorization: str | None,
    redis: aioredis.Redis,
) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
        )

    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        ) from exc

    jti = payload.get("jti")
    if not jti or not await redis.get(ALLOWLIST_KEY.format(jti=jti)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token revoked",
        )

    return payload


@router.api_route(
    "/auth/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def proxy_auth(path: str, request: Request) -> Response:
    return await _forward(
        request.app.state.http_client,
        request,
        settings.auth_service_url,
        f"auth/{path}",
    )


@router.get("/feed")
async def proxy_feed(request: Request) -> Response:
    await authorize_feed_request(
        request.headers.get("authorization"),
        request.app.state.redis,
    )
    return await _forward(
        request.app.state.http_client,
        request,
        settings.feed_service_url,
        "feed",
    )
