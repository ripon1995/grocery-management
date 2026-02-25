from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    scheme_name="JWT Bearer",
    description="JWT Authorization header using the Bearer scheme",
    auto_error=True
)
