from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router
from app.core.exception_handlers import register_exception_handlers
from app.core.log_config import configure_logging
from app.core.openapi_config import custom_openapi
from app.middleware.request_logger import RequestLoggerMiddleware

# ── Logging ────────────────────────────────────────────────────────────────
# step logger
configure_logging(level=settings.LOG_LEVEL, environment=settings.ENVIRONMENT)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code here if needed
    print("Application startup complete ✓")
    yield
    print("Application shutdown complete ✓")
    # shutdown code here if needed


app = FastAPI(
    title='Grocery Helper APIs',
    description="API for managing groceries and shopping lists",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

# Custom OpenAPI
app.openapi = lambda: custom_openapi(app=app)

# ── Middleware ──────────────────────────────────────────────────────────────
# request logger middleware
app.add_middleware(RequestLoggerMiddleware, env_name=settings.ENVIRONMENT)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,  # Which domains can talk to the API
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ── Exception handlers ──────────────────────────────────────────────────────
register_exception_handlers(app)


# ── Root endpoint ───────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def welcome() -> dict:
    return {"Hello": "Chief"}


# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix='/api')
