
from flask import Blueprint, request, jsonify
from ..models.prod_grp import ProdGrp
from main import db
from flask_jwt_extended import jwt_required

prod_grp_bp = Blueprint("prod_grp", __name__)

@prod_grp_bp.route("/", methods=["GET"])
@jwt_required()
def list_prod_grp():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    pagination = ProdGrp.query.paginate(page=page, per_page=per_page, error_out=False)
    data = [obj.__dict__ for obj in pagination.items]
    for d in data:
        d.pop("_sa_instance_state", None)
    return jsonify({
        "items": data,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    })

@prod_grp_bp.route("/", methods=["POST"])
@jwt_required()
def create_prod_grp():
    d = request.json
    obj = ProdGrp(**d)
    db.session.add(obj)
    db.session.commit()
    return jsonify({"id": getattr(obj, 'id', None)}), 201
