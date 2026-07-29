from datetime import datetime
from flask import Blueprint, current_app, request

from api_app.modules.utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from sqlalchemy.orm import joinedload, selectinload
from ..models.product_model import Product

product_bp = Blueprint("product", __name__)

@product_bp.route("/l", methods=["POST"])
@firebase_auth_required
#@swag_from(product_docs["list_product"])
def list_product():
    try:
        data = request.get_json() or {}
        uid = data.get("u")
        description = data.get("d")
        is_active = data.get("ia")
        is_combo = data.get("ic")
        barcode = data.get("b")
        internal_code = data.get("ic", None)
        organization_uid = data.get("ou", None)
        main_organization_uid = data.get("mou", None)
        count_table = True if data.get("ct") == "1" else False  # 1 for True, 0 for False
        sale_tables = True if data.get("st") == "1" else False  # 1 for True, 0 for False
        complementary_tables = True if data.get("cyt") == "1" else False  # 1 for True, 0 for False
        page = int(data.get("p", 1))
        per_page = int(data.get("pp", 10))
        order_by = data.get("ob", "description")  # Default order by description

        query = Product.query

        if uid not in (None, ""):
            query = query.filter(Product.uid == uid)
        if description not in (None, ""):
            query = query.filter(Product.description.ilike(f"%{description}%"))
        if is_active not in (None, ""):
            query = query.filter(Product.is_active == is_active)
        if barcode not in (None, ""):
            query = query.filter(Product.barcode == barcode)
        if internal_code not in (None, ""):
            query = query.filter(Product.internal_code == internal_code)
        if main_organization_uid not in (None, ""):
            query = query.filter(Product.main_organization_uid_fk == main_organization_uid)
            
        query = query.filter(Product.organization_uid_fk == organization_uid).order_by(getattr(Product, order_by).asc())

        if count_table:
            query = query.options(selectinload(Product.product_count))

        if sale_tables:
            query = query.options(selectinload(Product.product_brand))
            query = query.options(selectinload(Product.product_detail))
            query = query.options(selectinload(Product.product_category))
            #query = query.options(selectinload(Product.product_inventory))
            query = query.options(selectinload(Product.product_tax_info))
            query = query.options(selectinload(Product.product_unit))
            
        if complementary_tables:
            query = query.options(selectinload(Product.product_expiry))
            query = query.options(selectinload(Product.product_supplier))
            
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        items = []
        for product in pagination.items:
            if hasattr(product, "to_dict"):
                items.append(product.to_dict())
            else:
                # fallback if to_dict is missing
                items.append({
                    "uid": getattr(product, "uid", None),
                    "description": getattr(product, "description", None),
                    "is_active": getattr(product, "is_active", None),
                })

        return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = data,
                    total = pagination.total,
                    page = pagination.page,
                    pages = pagination.pages
                )

    except Exception as e:
        import traceback
        current_app.logger.debug(f"Product list error: {traceback.format_exc()}")
        return json_response(
            response=ApiResponse.INTERNAL_ERROR,
            data={"error": str(e)}
        ), 500