# Keep `main.py` focused on the application factory and registration.
# Do not create a module-level `app` here to avoid import-time side effects.

from flask import Flask, app
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger

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

db = SQLAlchemy()
jwt = JWTManager()
swagger = Swagger(template=swagger_template) # adds authorization header to all endpoints 
#swagger = Swagger()

import sys
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Ensure api_app is discoverable
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)
    migrate = Migrate(app, db)
    
    from api_app.modules.person.routes.address_route import address_bp
    app.register_blueprint(address_bp, url_prefix='/address')

    #from api_app.modules.country.country_route import country_bp
    #app.register_blueprint(country_bp, url_prefix='/country')

    from api_app.modules.utils.error_codes_route import errors_bp
    app.register_blueprint(errors_bp, url_prefix='/errors')

    # Initialize Firebase admin SDK (reads env or security file)
    from api_app.modules.auth_firebase.firebase_services import init_app as init_firebase
    init_firebase(app)

    from test_health import health_bp
    app.register_blueprint(health_bp, url_prefix='/health')

    from api_app.modules.person.routes.mail_route import mail_bp
    app.register_blueprint(mail_bp, url_prefix='/mail')
    
    from api_app.modules.person.routes.phone_route import phone_bp
    app.register_blueprint(phone_bp, url_prefix='/phone')

    from api_app.modules.users.routes.organization_route import organization_bp
    app.register_blueprint(organization_bp, url_prefix='/organization')

    from api_app.modules.acl.acl_decorator import permissions_bp
    app.register_blueprint(permissions_bp, url_prefix='/permissions')

    from api_app.modules.person.routes.person_route import person_bp
    app.register_blueprint(person_bp, url_prefix='/person')
    
    from api_app.modules.person.routes.person_natural_route import person_natural_bp
    app.register_blueprint(person_natural_bp, url_prefix='/personnatural')

    from api_app.modules.person.routes.person_legal_route import person_legal_bp
    app.register_blueprint(person_legal_bp, url_prefix='/personlegal')

    from api_app.modules.product.routes.product_route import product_bp
    app.register_blueprint(product_bp, url_prefix='/product')    
 
    from api_app.modules.sync.sync_route import sync_bp
    app.register_blueprint(sync_bp, url_prefix='/sync')
 
    from api_app.modules.users.routes.user_organizations_route import user_organizations_bp
    app.register_blueprint(user_organizations_bp, url_prefix='/u_orgs')
 
    from api_app.modules.users.routes.users_route import users_bp
    app.register_blueprint(users_bp, url_prefix='/users')
    
    from api_app.modules.users.routes.users_roles_route import users_roles_bp
    app.register_blueprint(users_roles_bp, url_prefix='/roles')

    return app