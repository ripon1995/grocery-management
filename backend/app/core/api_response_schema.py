from datetime import datetime, timezone
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponseSchema(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=lambda _: datetime.now(timezone.utc))
    data: Optional[T] = None
