"""WSGI entrypoint: create the Flask app from the factory and expose it.

This module keeps the entrypoint responsibility separate from
application configuration and blueprint registration (which live in
`main.py`). Hosting providers can import `app` or `application` from
here: `from run import app as application`.
"""
from main import create_app

# Create the app at import time for WSGI servers that expect a ready app
# while keeping the configuration and registration inside `create_app`.
app = create_app()
application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
