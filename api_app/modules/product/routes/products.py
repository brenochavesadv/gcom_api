from flask import Blueprint, request, jsonify
from ..models.products import Products
from main import db
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from ..docs.products import products_docs

products_bp = Blueprint("products", __name__)

@products_bp.route("/", methods=["GET"])
@jwt_required()
@swag_from(products_docs['create_product'])
def list_products():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    order_by = request.args.get("order_by", "produtos_id")
    direction = request.args.get("direction", "asc")

    query = Products.query
    if "descr" in request.args:
        query = query.filter(Products.descr.like(f"%{request.args['descr']}%"))
    if "ativo" in request.args:
        query = query.filter(Products.ativo == request.args["ativo"])
    if "prod_grp_id_fk" in request.args:
        query = query.filter(Products.prod_grp_id_fk == request.args["prod_grp_id_fk"])
    if "codprod" in request.args:
        query = query.filter(Products.codprod == request.args["codprod"])

    if hasattr(Products, order_by):
        column = getattr(Products, order_by)
        query = query.order_by(column.desc() if direction == "desc" else column.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    data = [{
        "produtos_id": p.produtos_id,
        "codprod": p.codprod,
        "descr": p.descr,
        "tam": float(p.tam)
    } for p in pagination.items]
    return jsonify({
        "items": data,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    })

@products_bp.route("/", methods=["POST"])
@jwt_required()
@swag_from({

})
def create_product():
    d = request.json
    item = Products(**d)
    db.session.add(item)
    db.session.commit()
    return jsonify({"id": item.produtos_id}), 201
