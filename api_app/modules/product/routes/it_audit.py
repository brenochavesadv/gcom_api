from flask import Blueprint, request, jsonify
from ..models.it_audit import ItAudit
from main import db
from flask_jwt_extended import jwt_required

it_audit_bp = Blueprint("it_audit", __name__)

@it_audit_bp.route("/", methods=["GET"])
@jwt_required()
def list_it_audit():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    pagination = ItAudit.query.paginate(page=page, per_page=per_page, error_out=False)
    data = [obj.__dict__ for obj in pagination.items]
    for d in data:
        d.pop("_sa_instance_state", None)
    return jsonify({
        "items": data,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    })

@it_audit_bp.route("/", methods=["POST"])
@jwt_required()
def create_it_audit():
    d = request.json
    obj = ItAudit(**d)
    db.session.add(obj)
    db.session.commit()
    return jsonify({"id": getattr(obj, 'id', None)}), 201
