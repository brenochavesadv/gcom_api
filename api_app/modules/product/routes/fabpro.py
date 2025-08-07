
from flask import Blueprint, request, jsonify
from ..models.fabpro import Fabpro
from main import db
from flask_jwt_extended import jwt_required
from flasgger import swag_from

fabpro_bp = Blueprint("fabpro", __name__)

@fabpro_bp.route("/", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Fabpro'],
    'responses': {
        200: {
            'description': 'List of Fabpro',
            'schema': {
                'type': 'object',
                'properties': {
                    'items': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'fabpro_id': {'type': 'integer'},
                                'instit_id_fk': {'type': 'integer'},
                                'marca': {'type': 'string'},
                                'fabr': {'type': 'string'}
                            }
                        }
                    },
                    'total': {'type': 'integer'},
                    'page': {'type': 'integer'},
                    'pages': {'type': 'integer'}
                }
            }
        }
    }
})
def list_fabpro():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    pagination = Fabpro.query.paginate(page=page, per_page=per_page, error_out=False)
    data = [obj.__dict__ for obj in pagination.items]
    for d in data:
        d.pop("_sa_instance_state", None)
    return jsonify({
        "items": data,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    })

@fabpro_bp.route("/", methods=["POST"])
@jwt_required()
def create_fabpro():
    d = request.json
    obj = Fabpro(**d)
    db.session.add(obj)
    db.session.commit()
    return jsonify({"id": getattr(obj, 'id', None)}), 201
