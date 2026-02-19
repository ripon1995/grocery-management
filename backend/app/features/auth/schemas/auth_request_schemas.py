from pydantic import BaseModel, Field


class UserCreateRequestSchema(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=30,
        description='Username'
    )
    email: str = Field(
        min_length=6,
        max_length=50,
        description='Email'
    )
    password: str = Field(
        min_length=6,
        max_length=50,
        description='Password'
    )
