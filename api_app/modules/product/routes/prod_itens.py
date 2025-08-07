
from flask import Blueprint, request, jsonify
from ..models.prod_itens import ProdItens
from main import db
from flask_jwt_extended import jwt_required

prod_itens_bp = Blueprint("prod_itens", __name__)

@prod_itens_bp.route("/", methods=["GET"])
@jwt_required()
def list_prod_itens():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    pagination = ProdItens.query.paginate(page=page, per_page=per_page, error_out=False)
    data = [obj.__dict__ for obj in pagination.items]
    for d in data:
        d.pop("_sa_instance_state", None)
    return jsonify({
        "items": data,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    })

@prod_itens_bp.route("/", methods=["POST"])
@jwt_required()
def create_prod_itens():
    d = request.json
    obj = ProdItens(**d)
    db.session.add(obj)
    db.session.commit()
    return jsonify({"id": getattr(obj, 'id', None)}), 201
