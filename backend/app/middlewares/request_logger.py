import logging
from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware


log = logging.getLogger("cyberley.request")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = perf_counter()
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (perf_counter() - start) * 1000
            log.exception("%s %s -> error (%.1f ms) request_id=%s", request.method, request.url.path, elapsed_ms, request_id)
            raise
        elapsed_ms = (perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
        log.info("%s %s -> %s (%.1f ms) request_id=%s", request.method, request.url.path, response.status_code, elapsed_ms, request_id)
        return response
