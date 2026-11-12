# Keep `main.py` focused on the application factory and registration.
# Do not create a module-level `app` here to avoid import-time side effects.

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from dotenv import dotenv_values
from backend.config import Config
from backend.extensions import db, jwt, migrate, swagger
import logging

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Sua API",
        "description": "Documentação da API",
        "version": "1.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Adicione 'Bearer <seu_token>'"
        }
    }
}

db = db
jwt = jwt
swagger = Swagger(template=swagger_template)  # adds authorization header to all endpoints

# Do not touch `app.logger` at import time. The real logger exists only after create_app().
import sys
import os

logging.basicConfig(level=logging.DEBUG)

# Variável global para o caminho da raiz do projeto
root_path = os.path.abspath(os.path.dirname(__file__))
env_values = dotenv_values(dotenv_path=os.path.join(root_path, ".env"))
environment_mode = env_values.get("FLASK_ENV", "production")
data_path = os.path.join(root_path, "instance", "data")  # path for data storage folder
db_name = "db_tributos"  # default database name


if not os.path.exists(data_path):
    os.makedirs(data_path)
    
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if app.debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)

    # Ensure api_app is discoverable
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)
    migrate = Migrate(app, db)

    from backend.modules.auth_firebase.firebase_services import init_app as init_firebase
    init_firebase(app)

    from backend.modules.person.routes.address_route import address_bp
    app.register_blueprint(address_bp, url_prefix='/address')

    from backend.modules.product.routes.product_brand_route import product_brand_bp  
    app.register_blueprint(product_brand_bp, url_prefix='/brand')

    from backend.modules.product.routes.product_category_route import product_category_bp  
    app.register_blueprint(product_category_bp, url_prefix='/category') 

    from backend.modules.financial.routes.account_route import financial_bp
    app.register_blueprint(financial_bp, url_prefix='/financial')

    from backend.test_health import health_bp
    app.register_blueprint(health_bp, url_prefix='/health')

    from backend.modules.mail.smtp_routes import mail_bp
    app.register_blueprint(mail_bp, url_prefix='/mail')

    from backend.modules.users.routes.organization_route import organization_bp
    app.register_blueprint(organization_bp, url_prefix='/organization')

    from backend.modules.person.routes.mail_route import mail_bp
    app.register_blueprint(mail_bp, url_prefix='/pmail')
    
    from backend.modules.person.routes.phone_route import phone_bp
    app.register_blueprint(phone_bp, url_prefix='/phone')

    from backend.modules.acl.acl_decorator import permissions_bp
    app.register_blueprint(permissions_bp, url_prefix='/permissions')

    from backend.modules.person.routes.person_route import person_bp
    app.register_blueprint(person_bp, url_prefix='/person')

    from backend.modules.product.routes.product_route import product_bp
    app.register_blueprint(product_bp, url_prefix='/product')           
    
    from backend.modules.users.routes.user_profiles_route import user_profiles_bp
    app.register_blueprint(user_profiles_bp, url_prefix='/profiles')
    
    from backend.modules.users.routes.user_roles_route import users_roles_bp
    app.register_blueprint(users_roles_bp, url_prefix='/roles')

    from backend.modules.sync.sync_route import sync_bp
    app.register_blueprint(sync_bp, url_prefix='/sync')
    
    from backend.modules.product.tax_br.tax_br_route import tax_br_bp
    app.register_blueprint(tax_br_bp, url_prefix='/tax_br')

    from backend.modules.users.routes.user_organizations_route import user_organizations_bp
    app.register_blueprint(user_organizations_bp, url_prefix='/u_orgs')

    from backend.modules.unit.unit_route import unit_bp
    app.register_blueprint(unit_bp, url_prefix='/unit')

    from backend.modules.vehycles.routes.vehycles_routes import vehycles_bp
    app.register_blueprint(vehycles_bp, url_prefix='/vehycles')

    return app
