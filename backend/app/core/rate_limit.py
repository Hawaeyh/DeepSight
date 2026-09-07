from collections import defaultdict, deque
from threading import Lock
from time import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings


_requests: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def route_limit(path: str) -> int | None:
    if path in {"/api/v1/auth/login", "/api/v1/auth/google", "/api/v1/auth/firebase"}: return settings.RATE_LIMIT_LOGIN_PER_MINUTE
    if path == "/api/v1/guest/session": return settings.RATE_LIMIT_GUEST_PER_MINUTE
    if path in {"/api/v1/analysis/image", "/api/v1/videos", "/api/v1/extension/videos/frames"}: return settings.RATE_LIMIT_UPLOAD_PER_MINUTE
    if path.startswith("/api/v1/webcam/sessions/") and path.endswith("/frames"): return settings.RATE_LIMIT_UPLOAD_PER_MINUTE
    if path.startswith("/api/v1/reports/"): return settings.RATE_LIMIT_REPORT_PER_MINUTE
    return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        limit = route_limit(request.url.path) if settings.RATE_LIMIT_ENABLED else None
        if limit is None: return await call_next(request)
        identity = request.client.host if request.client else "unknown"
        key = f"rate:{request.url.path}:{identity}"
        allowed = self._redis_allowed(key, limit) if settings.APP_ENV in {"staging", "production"} and settings.REDIS_URL else self._memory_allowed(key, limit)
        if not allowed: return JSONResponse(status_code=429, content={"detail": {"code": "RATE_LIMITED", "message": "Too many requests. Try again shortly."}}, headers={"Retry-After": "60"})
        return await call_next(request)

    @staticmethod
    def _memory_allowed(key: str, limit: int) -> bool:
        now = time()
        with _lock:
            bucket = _requests[key]
            while bucket and bucket[0] <= now - 60: bucket.popleft()
            if len(bucket) >= limit: return False
            bucket.append(now); return True

    @staticmethod
    def _redis_allowed(key: str, limit: int) -> bool:
        try:
            from redis import Redis
            client = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=0.5, socket_timeout=0.5)
            count = client.incr(key)
            if count == 1: client.expire(key, 60)
            return count <= limit
        except Exception:
            return False
