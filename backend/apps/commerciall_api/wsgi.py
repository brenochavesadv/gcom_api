"""WSGI entrypoint for the Commerciall API."""

from backend.apps.commerciall_api.app import create_app


app = create_app()
application = app

