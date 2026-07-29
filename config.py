"""Application configuration for database, JWT, and Swagger settings.

Database credentials are loaded differently depending on ``environment_mode``:
production accepts either a JSON file path or an inline JSON string, while
development reads the local ``security/db_development.json`` file.
"""

import json
import logging
import os
from main import root_path, env_values, environment_mode

logger = logging.getLogger(__name__)

def db_info(json_data):
    """Extract and validate the database credential and server URL."""

    key = json_data.get("key") if isinstance(json_data, dict) else None
    url = json_data.get("url") if isinstance(json_data, dict) else None

    if not key or not url:
        raise RuntimeError("Database missing in the provided information.")

    return key, url

class Config:
    """Base Flask configuration shared by the application."""

    # Flask-SQLAlchemy bind mappings are populated for the active environment.
    binds = {}
    SQLALCHEMY_BINDS = {}

    # Keep the environment-provided value available when running in production.
    db_main = env_values.get("DB_MAIN") if environment_mode == "production" else None

    logger.debug(f"Running in {environment_mode} environment.")

    if environment_mode == "production":

        # DB_MAIN may contain a path to a JSON file or the JSON document itself.
        db_main = os.environ.get("DB_MAIN")
        #binds['DB_FROTALL'] = 'db_frotall.json'

        if db_main:
            json_path = os.path.expanduser(db_main)
            json_path = os.path.abspath(json_path)
            if os.path.exists(json_path):
                # Load credentials from the referenced JSON file.
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                try:
                    data = json.loads(db_main)
                except Exception:
                    data = None

        # Expected production fields: "key" and "url".
        key = data.get("key") if isinstance(data, dict) else None
        url = data.get("url") if isinstance(data, dict) else None

        # Configure both the default database and its named SQLAlchemy bind.
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{key}@{url}"
        SQLALCHEMY_BINDS['DB_MAIN'] = f"mysql+pymysql://{key}@{url}"

    else:

        # Development credentials are loaded from the local security directory.
        path = os.path.join(root_path, "security", "db_development.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                db_info = json.load(f)
        except FileNotFoundError:
                raise RuntimeError(f"Development Database information not found: db_development.json")

        key = db_info.get("key") if isinstance(db_info, dict) else None
        url_main = db_info.get("url_main") if isinstance(db_info, dict) else None
        url_frotall = db_info.get("url_frotall") if isinstance(db_info, dict) else None

        if not key or not url_main:
            raise RuntimeError("Development Database missing in the provided information.")

        # Use the main development database as the default and named bind.
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{key}@{url_main}"
        SQLALCHEMY_BINDS['DB_MAIN'] = f"mysql+pymysql://{key}@{url_main}"
        #SQLALCHEMY_BINDS['DB_FROTALL'] = f"mysql+pymysql://{key}@{url_frotall}"

        logger.debug(f"Database information loaded successfully for development: {url_main}")

    # Disable the legacy event system to avoid unnecessary overhead.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # JWT_SECRET_KEY should be supplied by the environment outside development.
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecret")
    # Flasgger/OpenAPI UI metadata.
    SWAGGER = {
        'title': "Flask API",
        'uiversion': 3
    }
