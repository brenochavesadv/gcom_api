"""Shared configuration for all Flask applications in the monorepo."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")


def _application_name(value: Optional[str]) -> str:
    """Resolve an application package from Flask's ``module:factory`` value."""
    raw_value = (value or "commerciall_api").split(":", 1)[0].strip()
    parts = [part for part in raw_value.split(".") if part]

    if len(parts) >= 3:
        return parts[-2]
    return parts[-1] if parts else "commerciall_api"


class LegacyConfig:
    """Base configuration shared by local development and WSGI servers."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-development")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BACKEND_DIR / 'instance' / 'data' / 'db_commerciall.sqlite3'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False


# Canonical configuration for the monorepo.
import json
import logging

from dotenv import dotenv_values


BACKEND_DIR = Path(__file__).resolve().parent
APP_NAME = _application_name(os.getenv("FLASK_APP"))
APP_ENV = BACKEND_DIR / "apps" / APP_NAME / ".env"
ENV_VALUES = dotenv_values(APP_ENV if APP_ENV.exists() else BACKEND_DIR / ".env")
ENVIRONMENT = os.getenv("FLASK_ENV", ENV_VALUES.get("FLASK_ENV", "production"))
logger = logging.getLogger(__name__)


def _database_uri():
    if ENVIRONMENT != "production":
        path = BACKEND_DIR / "security" / "db_development.json"
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        key = data.get("key")
        url = data.get("url_main")
    else:
        raw = os.getenv("DB_MAIN", ENV_VALUES.get("DB_MAIN"))
        if not raw:
            return os.getenv("DATABASE_URL", "sqlite:///instance/data/app.sqlite3")
        path = Path(os.path.expanduser(raw))
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else json.loads(raw)
        key = data.get("key")
        url = data.get("url")

    if not key or not url:
        raise RuntimeError("Database configuration is missing key or URL.")
    return f"mysql+pymysql://{key}@{url}"


class CanonicalConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", ENV_VALUES.get("SECRET_KEY", "change-me-in-development"))
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", ENV_VALUES.get("JWT_SECRET_KEY", "jwtsecret"))
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_BINDS = {"DB_MAIN": SQLALCHEMY_DATABASE_URI}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER = {"title": "Flask API", "uiversion": 3}



"""Application configuration for database, JWT, and Swagger settings.

Database credentials are loaded differently depending on ``environment_mode``:
production accepts either a JSON file path or an inline JSON string, while
development reads the local ``security/db_development.json`` file.
"""

import json
import logging
import os
from dotenv import dotenv_values


root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
selected_app = os.getenv("FLASK_APP", "commerciall_api")
selected_app = _application_name(selected_app)
app_env_path = os.path.join(root_path, "apps", selected_app, ".env")
backend_env_path = os.path.join(root_path, ".env")
env_values = dotenv_values(
    dotenv_path=app_env_path if os.path.exists(app_env_path) else backend_env_path
)
environment_mode = os.getenv("FLASK_ENV", env_values.get("FLASK_ENV", "production"))

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

    if False:

        # DB_MAIN may contain a path to a JSON file or the JSON document itself.
        # ``env_values`` comes from the project .env file; dotenv_values does
        # not populate ``os.environ``.
        db_main = (
            os.environ.get("DB_MAIN")
            or env_values.get("DB_MAIN")
            or os.path.join(root_path, "security", "db_main.json")
        )
        data = None
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
        key, url = db_info(data) if isinstance(data, dict) else (None, None)

        if not key or not url:
            raise RuntimeError("Production Database missing in the provided information.")

        # Configure both the default database and its named SQLAlchemy bind.
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{key}@{url}"
        SQLALCHEMY_BINDS['DB_MAIN'] = f"mysql+pymysql://{key}@{url}"

    elif False:

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
    SECRET_KEY = os.getenv("SECRET_KEY", env_values.get("SECRET_KEY", "change-me-in-development"))
    # JWT_SECRET_KEY should be supplied by the environment outside development.
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", env_values.get("JWT_SECRET_KEY", "jwtsecret"))
    # Flasgger/OpenAPI UI metadata.
    SWAGGER = {
        'title': "Flask API",
        'uiversion': 3
    }


Config = CanonicalConfig
