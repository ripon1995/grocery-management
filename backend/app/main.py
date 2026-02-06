from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(title='Grocery Helper APIs')


@app.get("/")
def welcome():
    return {"Hello": "Chief"}


app.include_router(api_router, prefix='/api')
