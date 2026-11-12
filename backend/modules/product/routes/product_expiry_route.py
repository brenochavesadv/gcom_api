from flask import Blueprint, current_app, request
from backend.modules.utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from ..models.product_expiry_model import ProductExpiry

product_bp = Blueprint("product", __name__)

@product_bp.route("/expiry/l", methods=["POST"])
@firebase_auth_required
#@swag_from(product_docs["list_product"])
def list_expiry():
    try:
        data = request.get_json() or {}
        product_uid = data.get("pu")

        if product_uid in (None, ""):
            return json_response(response="MISSING_FIELDS")

        query = ProductExpiry.query.filter(ProductExpiry.product_uid_fk == product_uid)

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
