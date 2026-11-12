"""Backward-compatible imports for the Tributos API."""

from backend.apps.tributos_api.app import create_app
from backend.config import (
    BACKEND_DIR as root_path,
    Config,
    ENV_VALUES as env_values,
    ENVIRONMENT as environment_mode,
)
from backend.extensions import db, jwt, migrate, swagger
data_path = root_path / "instance" / "data"
from backend.extensions import db, jwt, migrate, swagger


__all__ = ["create_app", "db", "jwt", "migrate", "swagger"]

