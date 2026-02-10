# src/middleware/simple_request_logger.py
import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# We'll get this logger from the root logger you already configured
logger = logging.getLogger("request")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, env_name: str = "development"):
        super().__init__(app)
        self.env_name = env_name

    async def dispatch(self, request: Request, call_next):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Log the incoming request
        logger.info(
            "%s | %s | %s | %s",
            timestamp,
            self.env_name.upper(),
            request.method,
            request.url.path
        )

        response: Response = await call_next(request)
        return response
