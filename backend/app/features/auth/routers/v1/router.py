from fastapi import APIRouter, status, Depends

from app.core.api_response_schema import ApiResponseSchema
from app.features.auth.dependencies import get_auth_service
from app.features.auth.schemas import (
    UserCreateRequestSchema,
    UserCreateResponseSchema,
    LoginResponseSchema,
    LoginRequestSchema,
    TokenRefreshResponseSchema,
    TokenRefreshRequestSchema,
)
from app.features.auth.service import AuthService

router = APIRouter(
    prefix="/v1/auth",
    tags=["auth"]
)


@router.post(
    "/register",
    response_model=ApiResponseSchema[UserCreateResponseSchema],
    summary='Create a new user',
    status_code=status.HTTP_201_CREATED
)
async def create_user(
        data: UserCreateRequestSchema,
        auth_service: AuthService = Depends(get_auth_service),

):
    response = await auth_service.register_user(data)
    return ApiResponseSchema(
        success=True,
        data=response,
        message='User created successfully',
    )


@router.post(
    "/login",
    response_model=ApiResponseSchema[LoginResponseSchema],
    summary='Login a user',
    status_code=status.HTTP_200_OK
)
async def login_user(
        data: LoginRequestSchema,
        auth_service: AuthService = Depends(get_auth_service)
):
    response = await auth_service.authenticate_user(data)
    return ApiResponseSchema(
        success=True,
        data=response,
        message='Login successful',
    )


@router.post(
    '/token-refresh',
    response_model=ApiResponseSchema[TokenRefreshResponseSchema],
    summary='Token refresh',
    status_code=status.HTTP_200_OK
)
async def token_refresh(
        data: TokenRefreshRequestSchema,
        auth_service: AuthService = Depends(get_auth_service)
):
    response = await auth_service.refresh_token(data)
    return ApiResponseSchema(
        success=True,
        data=response,
        message='Token refreshed successfully',
    )
