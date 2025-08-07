from flask import Flask
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

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)
    
    # Inicializa o Firebase

    from api_app.modules.auth_firebase.firebase_routes import firebase_bp
    app.register_blueprint(firebase_bp, url_prefix='/firebase')

    from api_app.modules.product.routes.aliquota import aliquota_bp
    app.register_blueprint(aliquota_bp, url_prefix='/aliquota')

    from api_app.modules.product.routes.fabpro import fabpro_bp
    app.register_blueprint(fabpro_bp, url_prefix='/fabpro')

    from api_app.modules.entity.entity_routes import entity_bp
    app.register_blueprint(entity_bp, url_prefix='/entity')
    
    from api_app.modules.product.routes.it_audit import it_audit_bp
    app.register_blueprint(it_audit_bp, url_prefix='/it_audit')
    
    from api_app.modules.product.routes.prod_grp import prod_grp_bp
    app.register_blueprint(prod_grp_bp, url_prefix='/prod_grp')
    
    from api_app.modules.product.routes.prod_itens import prod_itens_bp
    app.register_blueprint(prod_itens_bp, url_prefix='/prod_itens')
    
    from api_app.modules.product.routes.products import products_bp
    app.register_blueprint(products_bp, url_prefix='/products')
    
    from api_app.modules.person.routes.person_control import person_control_bp
    app.register_blueprint(person_control_bp, url_prefix='/personcontrol')
    
    from api_app.modules.person.routes.person_natural import person_natural_bp
    app.register_blueprint(person_natural_bp, url_prefix='/personnatural')

    from api_app.modules.acl.acl_decorator import permissions_bp
    app.register_blueprint(permissions_bp, url_prefix='/permissions')
    
    from api_app.modules.product.routes.unidades import unidades_bp
    app.register_blueprint(unidades_bp, url_prefix='/unidades')
    
    from api_app.modules.person.routes.users import users_bp
    app.register_blueprint(users_bp, url_prefix='/users')
    
    from api_app.modules.person.routes.users_group import users_group_bp
    app.register_blueprint(users_group_bp, url_prefix='/usersgroup')

    return app
