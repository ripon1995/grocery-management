from fastapi import APIRouter, status, Depends

from app.features.auth.dependencies import get_auth_service
from app.features.auth.schemas import UserCreateRequestSchema, UserCreateResponseSchema
from app.features.auth.service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post(
    "/register",
    response_model=UserCreateResponseSchema,
    summary='Create a new user',
    status_code=status.HTTP_201_CREATED
)
async def create_user(
        data: UserCreateRequestSchema,
        auth_service: AuthService = Depends(get_auth_service),

):
    return await auth_service.register_user(data)
