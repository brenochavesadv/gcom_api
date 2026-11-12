"""Shared Flask extension instances for every backend application."""

from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
swagger = Swagger()

