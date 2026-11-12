"""Centralized HTTP error handling for the Flask application."""

from flask import Flask, current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException

from backend.modules.utils.api_response import ApiResponse, json_response


def _rollback() -> None:
    # Import lazily to avoid a circular import while the Flask app is created.
    from backend.apps.commerciall_api.main import db

    db.session.rollback()


def response_for_exception(exc: Exception):
    """Rollback, log and build the standard response for an application error."""
    if isinstance(exc, HTTPException):
        return exc

    _rollback()
    current_app.logger.exception("Unhandled application error")

    if isinstance(exc, IntegrityError):
        response = ApiResponse.DUPLICATE_ENTRY
    elif isinstance(exc, SQLAlchemyError):
        response = ApiResponse.DB_CONFLICT
    else:
        response = ApiResponse.INTERNAL_ERROR

    return json_response(
        response=response,
        exception=type(exc).__name__,
    )


def register_error_handlers(app: Flask) -> None:
    """Register the application's exception-to-JSON mappings."""

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(exc: IntegrityError):
        return response_for_exception(exc)

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(exc: SQLAlchemyError):
        return response_for_exception(exc)

    @app.errorhandler(Exception)
    def handle_unexpected_error(exc: Exception):
        return response_for_exception(exc)
