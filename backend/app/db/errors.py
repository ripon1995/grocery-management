"""
Translate SQLAlchemy errors into app-level database exceptions.
Used by repositories so they don't repeat try/except in every method.
"""

from functools import wraps

from sqlalchemy.exc import SQLAlchemyError, TimeoutError, StatementError

from app.core.exceptions import DatabaseException, DatabaseTimeoutException, DatabaseStatementTimeoutException


def handle_db_errors(message: str = 'Database error'):
    """Roll back the session and re-raise DB errors as app exceptions.
    The decorated method must belong to a class with a `session` attribute.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except TimeoutError as e:  # pool checkout timeout; subclass of SQLAlchemyError, so catch it first
                await self.session.rollback()
                raise DatabaseTimeoutException() from e
            except StatementError as e:
                await self.session.rollback()
                raise DatabaseStatementTimeoutException() from e
            except SQLAlchemyError as e:
                await self.session.rollback()
                raise DatabaseException(message=message) from e

        return wrapper

    return decorator
