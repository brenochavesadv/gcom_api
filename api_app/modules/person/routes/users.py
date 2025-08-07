from flask import Blueprint, request, jsonify
from ..models.users import Users
from ..docs.users import users_docs
from main import db
from ...auth_firebase.firebase_decorators import auth_required
from flasgger import swag_from
from datetime import datetime

users_bp = Blueprint("users", __name__)

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
#@auth_required
@swag_from(users_docs["list_users"])
def list_users():
    try:
        id = int(request.args.get("id", 0))
        uid = request.args.get("uid")
        entity_id = int(request.args.get("entity_id", 0))
        name = request.args.get("name")
        group_id = request.args.get("users_group_id_fk")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        query = Users.query

        if id != 0:
            query = query.filter_by(id=id)
        elif uid is not None:
            query = query.filter_by(uid=uid)
        else:
            if entity_id is None:
                return jsonify({"error": "Entity ID is required"}), 200
            
            query = query.filter_by(entity_id_fk=entity_id)

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

