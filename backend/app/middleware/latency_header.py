from fastapi import Request
import time
from starlette.middleware.base import BaseHTTPMiddleware


class LatencyHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        latency = (time.time() - start_time) * 1000  # ms
        response.headers["X-Response-Time"] = f"{latency:.2}ms"
        return response