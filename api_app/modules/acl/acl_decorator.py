
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt
from functools import wraps
from flask import abort
from flasgger import swag_from
from api_app.modules.acl.acl_docs import permissions_doc  # Importa a documentação
from flask import Blueprint

permissions_bp = Blueprint("permissions", __name__)

@permissions_bp.route("/", methods=["GET"])
@jwt_required()
@swag_from(permissions_doc["list_permissions"])  # Usa a documentação importada

def permission_required(*permissions):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_perms = claims.get("permissions", [])
            if not any(perm in user_perms for perm in permissions):
                abort(403, description="Permissão negada")
            return fn(*args, **kwargs)
        return decorator
    return wrapper
