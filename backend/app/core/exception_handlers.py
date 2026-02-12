from fastapi import Request, FastAPI
from starlette.responses import JSONResponse

from app.core.exceptions import AppBaseException


def register_exception_handlers(app: FastAPI):
    """
    Registers all global exception handlers for the FastAPI application.
    Call this once during app startup.
    """

    @app.exception_handler(AppBaseException)
    async def app_base_exception_handler(request: Request, exc: AppBaseException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                'error_code': exc.error_code,
                'message': exc.message,
                'detail': exc.detail,
                'status': exc.status,
            }
        )
