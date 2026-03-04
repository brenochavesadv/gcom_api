
from flask import Blueprint, request, jsonify
from .users_group_model import UsersGroup
from main import db
from flask_jwt_extended import jwt_required

users_group_bp = Blueprint("usergroup", __name__)

@users_group_bp.route("/", methods=["GET"])
@jwt_required()
def list_users_grp():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    pagination = UserGroup.query.paginate(page=page, per_page=per_page, error_out=False)
    data = [obj.__dict__ for obj in pagination.items]
    for d in data:
        d.pop("_sa_instance_state", None)
    return jsonify({
        "items": data,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    })

@users_group_bp.route("/", methods=["POST"])
@jwt_required()
def create_user_grp():
    d = request.json
    obj = UserGroup(**d)
    db.session.add(obj)
    db.session.commit()
    return jsonify({"uid": getattr(obj, 'uid', None)}), 201
