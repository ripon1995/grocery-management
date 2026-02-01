from contextlib import asynccontextmanager
from fastapi import FastAPI
from .grocery.router import router as grocery_router
from .database.database_client import get_client, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_client()
    yield
    close_mongo_connection()


app = FastAPI(
    title='Grocery Helper APIs',
    lifespan=lifespan,
)


@app.get("/")
def welcome():
    return {"Hello": "Chief"}


app.include_router(grocery_router)
