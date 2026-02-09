from fastapi import FastAPI
from app.api.router import api_router
from app.core.exception_handlers import register_exception_handlers

app = FastAPI(title='Grocery Helper APIs')

register_exception_handlers(app)


@app.get("/")
def welcome():
    return {"Hello": "Chief"}


app.include_router(api_router, prefix='/api')
