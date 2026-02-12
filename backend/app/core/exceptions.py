from fastapi import status


class AppBaseException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = 'internal_server_error'
    detail = 'Internal Server Error'
    message = 'Internal Server Error'
    status = 'fail'

    def __init__(
            self,
            error_code: str = None,
            detail: str = None,
            message: str = None,
    ):
        if error_code is not None:
            self.error_code = error_code
        if detail is not None:
            self.detail = detail
        if message is not None:
            self.message = message


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
