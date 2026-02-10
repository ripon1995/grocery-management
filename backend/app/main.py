from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router
from app.core.exception_handlers import register_exception_handlers
from app.core.log_config import configure_logging
from app.middleware.request_logger import RequestLoggerMiddleware

# step logger
configure_logging(level=settings.LOG_LEVEL, environment=settings.ENVIRONMENT)

app = FastAPI(title='Grocery Helper APIs')

origins = [
    "http://localhost:5173",
]

# 2. Add the Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Which domains can talk to the API
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# request logger
app.add_middleware(RequestLoggerMiddleware, env_name=settings.ENVIRONMENT)

register_exception_handlers(app)


@app.get("/")
def welcome():
    return {"Hello": "Chief"}


app.include_router(api_router, prefix='/api')
