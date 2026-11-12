"""WSGI entrypoint for the Tributos API."""

from backend.apps.tributos_api.app import create_app


app = create_app()
application = app

