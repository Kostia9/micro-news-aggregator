from starlette.middleware.base import BaseHTTPMiddleware


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        pass
