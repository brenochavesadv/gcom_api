from flask import Blueprint, current_app, request
from sqlalchemy.orm import joinedload, selectinload
from backend.modules.utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from ..models.product_supplier_model import ProductSupplier

product_bp = Blueprint("product", __name__)

@product_bp.route("/supplier/l", methods=["POST"])
@firebase_auth_required
#@swag_from(product_docs["list_product"])
def list_supplier():
    try:
        data = request.get_json() or {}
        product_uid = data.get("pu")
        main_organization_uid_fk = data.get("mou")

        if product_uid in (None, "") or main_organization_uid_fk in (None, ""):
            return json_response(response="MISSING_FIELDS")

        query = ProductSupplier.query.filter(ProductSupplier.product_uid_fk == product_uid, ProductSupplier.main_organization_uid_fk == main_organization_uid_fk)
        query = query.options(selectinload(ProductSupplier.person))

        data = []
        for item in query.all():
            data.append(item.to_dict())

        return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = data,
        )

    except Exception as e:
        import traceback
        current_app.logger.debug(f"ProductSupplier list error: {traceback.format_exc()}")
        raise
