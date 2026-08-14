from uuid import UUID

from app.core.exceptions import InvalidUUIDException


def validate_uuid(value):
    try:
        return UUID(value)
    except (ValueError, TypeError) as e:
        raise InvalidUUIDException() from e
