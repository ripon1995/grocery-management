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
        start_time = time.perf_counter()

        # Log the incoming request
        logger.info(
            f"START | {timestamp} | {self.env_name.upper()} | {request.method} | {request.url.path}",
        )

        try:
            response: Response = await call_next(request)
            process_time = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"FINISHED | {request.method} | {request.url.path} | "
                f"Status: {response.status_code} | Duration: {process_time:.2f}ms")
            return response

        except Exception as e:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"FAILED | {request.method} | {request.url.path} | "
                f"Error: {type(e).__name__} | Duration: {process_time:.2f}ms"
            )
            raise e
