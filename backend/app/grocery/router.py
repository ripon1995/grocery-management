from fastapi import APIRouter

router = APIRouter(
    prefix="/grocery",
    tags=["Grocery"],
)


@router.get("/list")
def get_grocery_list():
    return {"message": "Should return grocery list"}
