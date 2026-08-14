from fastapi import status


class AppBaseException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = 'internal_server_error'
    detail = 'Internal Server Error'
    message = 'Internal Server Error'
    status = 'fail'

    def __init__(
            self,
            error_code: str | None = None,
            detail: str | None = None,
            message: str | None = None,
    ):
        if message is not None:
            self.message = message
        super().__init__(self.message)
        if error_code is not None:
            self.error_code = error_code
        if detail is not None:
            self.detail = detail


class ResourceNotFoundException(AppBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'resource_not_found'
    detail = 'Resource not found'
    message = 'Resource not found'


class InvalidUUIDException(AppBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'invalid_uuid'
    detail = 'Invalid UUID'
    message = 'Provided UUID is invalid'


class ConflictException(AppBaseException):
    status_code = status.HTTP_409_CONFLICT
    error_code = 'conflict'
    detail = 'Already exists'
    message = 'Already exists'


class UnauthorizedException(AppBaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = 'unauthorized'
    detail = 'Unauthorized'
    message = 'Invalid credentials'


class DatabaseException(AppBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'database_error'
    detail = 'Database error'
    message = 'Database error'
