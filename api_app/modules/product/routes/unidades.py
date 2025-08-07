
from flask import Blueprint, request, jsonify
from ..models.unidades import Unidades
from main import db
from flask_jwt_extended import jwt_required

unidades_bp = Blueprint("unidades", __name__)

@unidades_bp.route("/", methods=["GET"])
@jwt_required()
def list_unidades():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    pagination = Unidades.query.paginate(page=page, per_page=per_page, error_out=False)
    data = [obj.__dict__ for obj in pagination.items]
    for d in data:
        d.pop("_sa_instance_state", None)
    return jsonify({
        "items": data,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    })

@unidades_bp.route("/", methods=["POST"])
@jwt_required()
def create_unidades():
    d = request.json
    obj = Unidades(**d)
    db.session.add(obj)
    db.session.commit()
    return jsonify({"id": getattr(obj, 'id', None)}), 201
