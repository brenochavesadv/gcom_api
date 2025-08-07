from datetime import datetime
from shlex import join
from flask import Blueprint, request, jsonify
from ..models.person_control import PersonControl
from ..docs.person_control import person_control_docs
from ...auth_firebase.firebase_decorators import auth_required
from flasgger import swag_from

person_control_bp = Blueprint("personcontrol", __name__)

@person_control_bp.route("/list", methods=["GET"])
#@auth_required
@swag_from(person_control_docs["list_person_control"])
def list_person_control():
    try:
        id = request.args.get("id")
        name = request.args.get("name")
        is_active = request.args.get("is_active")
        is_supplier = request.args.get("is_supplier")
        type_ = request.args.get("type")
        entity_id = request.args.get("entity_id")
        id_number = request.args.get("id_number")

        if entity_id is None:
            return jsonify({"error": "Entity ID is required"}), 200
        
        query = PersonControl.query

        if id is not None:
            query = query.filter_by(id=id)
        if name is not None:
            query = query.filter(PersonControl.name.ilike(f"%{name}%"))
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        if is_supplier is not None:
            query = query.filter_by(is_supplier=is_supplier)
        if type_ is not None:
            query = query.filter_by(person_type=type_)
        if id_number is not None:
            query = query.filter_by(id_number=id_number)

        query = query.filter(PersonControl.entity_id_fk == entity_id).order_by(PersonControl.name.desc())

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Use model to_dict() methods
        data = []
        for person_control in pagination.items:
            control_data = person_control.to_dict()
            data.append(control_data)

        return jsonify({
            "items": data,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500