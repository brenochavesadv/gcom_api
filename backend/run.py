"""WSGI entrypoint: create the Flask app from the factory and expose it.

This module keeps the entrypoint responsibility separate from
application configuration and blueprint registration (which live in
`main.py`). Hosting providers can import `app` or `application` from
here: `from run import app as application`.
"""
import os
import sys
import importlib

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_APP = ""


def create_app(app_name=None):
    """Load an application factory from ``backend.apps.<name>.main``."""
    selected_app = app_name or os.getenv("FLASK_APP", DEFAULT_APP)
    module_name, separator, factory_name = selected_app.partition(":")
    if not separator:
        module_name = f"backend.apps.{selected_app}.app"
        factory_name = "create_app"

    module = importlib.import_module(module_name)
    factory = getattr(module, factory_name)
    return factory()


def _cli_app_name():
    """Return the application selected by the optional ``--app`` argument."""
    for index, argument in enumerate(sys.argv):
        if argument == "--app" and index + 1 < len(sys.argv):
            return sys.argv[index + 1]
    return None

# Create the app at import time for WSGI servers that expect a ready app
# while keeping the configuration and registration inside `create_app`.
app = create_app(_cli_app_name())
application = app

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
    )
