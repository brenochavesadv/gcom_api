from flask import Blueprint, request, jsonify
from ..docs.aliquota import aliquota_docs
from ..models.aliquota import Aliquota
from main import db
from flask_jwt_extended import jwt_required
from flasgger import swag_from

aliquota_bp = Blueprint("aliquota", __name__)

@aliquota_bp.route("/", methods=["GET"])
@jwt_required()
@swag_from(aliquota_docs["list_aliquotas"])  # Usa a documentação importada
def list_aliquotas():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    order_by = request.args.get("order_by", "aliquotas_id")
    direction = request.args.get("direction", "asc")

    query = Aliquota.query
    if "descr" in request.args:
        query = query.filter(Aliquota.descr.like(f"%{request.args['descr']}%"))
    if "created_after" in request.args:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(request.args["created_after"])
            query = query.filter(Aliquota.created_at >= dt)
        except:
            pass
    if "bematech" in request.args:
        query = query.filter(Aliquota.bematech == request.args["bematech"])

    if hasattr(Aliquota, order_by):
        column = getattr(Aliquota, order_by)
        query = query.order_by(column.desc() if direction == "desc" else column.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    data = [{
        "aliquotas_id": a.aliquotas_id,
        "instit_id_fk": a.instit_id_fk,
        "descr": a.descr,
        "bematech": a.bematech,
        "valor": float(a.valor) if a.valor else None
    } for a in pagination.items]
    return jsonify({
        "items": data,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    })

@aliquota_bp.route("/", methods=["POST"])
@jwt_required()
@swag_from(aliquota_docs["create_aliquota"])
def create_aliquota():
    d = request.json
    item = Aliquota(**d)
    db.session.add(item)
    db.session.commit()
    return jsonify({"id": item.aliquotas_id}), 201
