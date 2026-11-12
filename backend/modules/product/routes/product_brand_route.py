import traceback
import uuid
from backend.apps.commerciall_api.main import db

from datetime import datetime, timezone
from flask import Blueprint, current_app, request
from backend.modules.utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from ..models.product_brand_model import ProductBrand

product_brand_bp = Blueprint("brand", __name__)

@product_brand_bp.route("/l", methods=["POST"])
@firebase_auth_required
def list_brand():
    try:
        data = request.get_json() or {}
        uid = data.get("u")
        main_organization_uid_fk = data.get("mou")
        brand = data.get("b")
        print(f"Received data for brand listing: {data}")  # Debugging line to print the received data

        if main_organization_uid_fk in (None, ""):
            return json_response(response="MISSING_FIELDS")

        query = ProductBrand.query.filter(ProductBrand.main_organization_uid_fk == main_organization_uid_fk)

        if uid not in (None, ""):
            query = query.filter(ProductBrand.uid == uid)
        if brand not in (None, ""):
            query = query.filter(ProductBrand.brand == brand)

        query = query.order_by(ProductBrand.brand.asc()).all()  # Order by brand ascending

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
@product_brand_bp.route("/ui", methods=["POST"])
@firebase_auth_required
def upsert_brand():
    try:
        data = request.get_json()
        print (f"Received data for upsert brand: {data}")  # Debugging line to print the received data

        _brand = ProductBrand.from_json(data)

        if (_brand.main_organization_uid_fk in (None, "") or _brand.brand in (None, "")):
            current_app.logger.debug("Missing required fields: main_organization_uid_fk or brand")
            return json_response(
                response=ApiResponse.MISSING_FIELDS
            )

        _selected = ProductBrand.query.filter_by(uid=_brand.uid, main_organization_uid_fk=_brand.main_organization_uid_fk).first()

        if _selected:
            _selected.brand = _brand.brand
            _selected.factory = _brand.factory
            _selected.updated_at = datetime.now(timezone.utc)
            _selected.sync_status = "PENDING"
            
            message = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
            
        else:
            _brand.uid = str(uuid.uuid4())
            _brand.updated_at = datetime.now(timezone.utc)
            _brand.created_at = datetime.now(timezone.utc)
            _brand.sync_status = "PENDING"
            db.session.add(_brand)
            message = ApiResponse.CREATED_SUCCESSFULLY
            persisted = _brand

        db.session.commit()

        return json_response(
            response=message,
            data={"brand": persisted.to_dict()}
        )

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
