from flask import Blueprint, request, jsonify
from .users_docs import users_docs
from .users_model import Users
from main import db
from ..auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from datetime import datetime

users_bp = Blueprint("user", __name__)

def serialize_user(user):
   
    user_dict = user.__dict__.copy()
    user_dict.pop("_sa_instance_state", None)
    
    # Handle datetime fields
    for key, value in user_dict.items():
        if isinstance(value, datetime):
            user_dict[key] = value.isoformat() if value else None
        elif key == "is_active":
            user_dict[key] = True if value == 1 else False
        elif key == "is_developer":
            user_dict[key] = True if value == 1 else False
    return user_dict

@users_bp.route("/", methods=["GET"])
@firebase_auth_required
@swag_from(users_docs["list_users"])
def list_users():
    try:
        uid = int(request.args.get("uid", 0))
        uid = request.args.get("uid")
        organization_uid = int(request.args.get("organization_uid", 0))
        name = request.args.get("name")
        group_id = request.args.get("users_group_id_fk")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        query = Users.query

        if uid != 0:
            query = query.filter_by(uid=uid)
        elif uid is not None:
            query = query.filter_by(uid=uid)
        else:
            if organization_uid is None:
                return jsonify({"error": "Entity ID is required"}), 200
            
            query = query.filter_by(organization_uid_fk=organization_uid)

            if name is not None:
                query = query.filter(Users.name.ilike(f"%{name}%"))
            elif group_id is not None:
                query = query.filter_by(users_group_id_fk=group_id)

        pagination = query.order_by(Users.name.desc()).paginate(page=page, per_page=per_page, error_out=False)

        data = [serialize_user(obj) for obj in pagination.items]
        
        return jsonify({
            "items": data,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
