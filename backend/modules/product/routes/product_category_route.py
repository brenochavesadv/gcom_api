import traceback
import uuid
from backend.apps.commerciall_api.main import db

from datetime import datetime, timezone
from flask import Blueprint, current_app, request
from backend.modules.utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from ..models.product_category_model import ProductCategory

product_category_bp = Blueprint("category", __name__)

@product_category_bp.route("/l", methods=["POST"])
@firebase_auth_required
def list_category():
    try:
        data = request.get_json() or {}
        uid = data.get("u")
        main_organization_uid_fk = data.get("mou")
        pt_br = data.get("pt_br")
        print(f"Received data for category listing: {data}")  # Debugging line to print the received data

        if main_organization_uid_fk in (None, ""):
            return json_response(response="MISSING_FIELDS")

        query = ProductCategory.query.filter(ProductCategory.main_organization_uid_fk == main_organization_uid_fk)

        if uid not in (None, ""):
            query = query.filter(ProductCategory.uid == uid)
        if pt_br not in (None, ""):
            query = query.filter(ProductCategory.pt_br == pt_br)

        query = query.order_by(ProductCategory.pt_br.asc()).all()  # Order by pt_br ascending

        data = []
        for item in query:
            data.append(item.to_dict())

        return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = data,
        )

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
@product_category_bp.route("/ui", methods=["POST"])
@firebase_auth_required
def upsert_category():
    try:
        data = request.get_json()
        print (f"Received data for upsert: {data}")  # Debugging line to print the received data

        _category = ProductCategory.from_json(data)

        if (_category.main_organization_uid_fk in (None, "")):
            current_app.logger.debug("Missing required fields: main_organization_uid_fk")
            return json_response(
                response=ApiResponse.MISSING_FIELDS
            )

        _selected = ProductCategory.query.filter_by(uid=_category.uid, main_organization_uid_fk=_category.main_organization_uid_fk).first()

        if _selected:
            _selected.pt_br = _category.pt_br
            _selected.updated_at = datetime.now(timezone.utc)
            _selected.sync_status = "PENDING"
            
            message = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
            
        else:
            _category.uid = str(uuid.uuid4())
            _category.updated_at = datetime.now(timezone.utc)
            _category.created_at = datetime.now(timezone.utc)
            _category.sync_status = "PENDING"
            db.session.add(_category)
            message = ApiResponse.CREATED_SUCCESSFULLY
            persisted = _category

        db.session.commit()

        return json_response(
            response=message,
            data={"category": persisted.to_dict()}
        )

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
