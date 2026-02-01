from fastapi import FastAPI
from .grocery.router import router as grocery_router

app = FastAPI(title='Grocery Helper APIs')


@app.get("/")
def welcome():
    return {"Hello": "Chief"}


app.include_router(grocery_router)
