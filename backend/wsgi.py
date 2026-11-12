"""WSGI-compatible application module."""

from backend.apps.commerciall_api.main import create_app


app = create_app()
application = app

