from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserCreateResponseSchema(BaseModel):
    id: UUID
    username: str
    email: str

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda x: str(x)
        }
    )
