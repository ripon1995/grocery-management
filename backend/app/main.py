from fastapi import FastAPI
from app.core.config import settings
from app.api.router import api_router
from app.core.exception_handlers import register_exception_handlers
from app.core.log_config import setup_stdlib_colored_logging

app = FastAPI(title='Grocery Helper APIs')

setup_stdlib_colored_logging(level=settings.LOG_LEVEL, for_dev=settings.DEBUG)

register_exception_handlers(app)


@app.get("/")
def welcome():
    return {"Hello": "Chief"}


app.include_router(api_router, prefix='/api')
