from datetime import datetime
from flask import Blueprint, request, jsonify
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from ..docs.product_docs import product_docs
from ..models.product_model import Product
from ..models.product_detail_model import ProductDetail


product_bp = Blueprint("product", __name__)

def _get_int_arg(name, default=None):
    val = request.args.get(name)
    if val is None or val == "":
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

@product_bp.route("/list", methods=["GET"])
@firebase_auth_required
#@swag_from(product_docs["list_product"])
def list_product():
    try:
        uid = _get_int_arg("uid", None)
        description = request.args.get("description")
        is_active = request.args.get("is_active")
        barcode = request.args.get("barcode")
        internal_code = _get_int_arg("internal_code", None)
        organization_uid = _get_int_arg("organization_uid", None)
        limit = _get_int_arg("limit", None)

        if organization_uid is None:
            return jsonify({"error": "Entity ID is required"}), 400

        # Query full Product instances so we can call to_dict()
        query = Product.query

        if uid is not None:
            query = query.filter(Product.uid == uid)
        if description:
            query = query.filter(Product.description.ilike(f"%{description}%"))
        if is_active is not None:
            is_active_val = 2 if str(is_active).lower() in ["true", "1"] else 1
            query = query.filter(Product.is_active == is_active_val)
        if barcode:
            query = query.filter(Product.barcode == barcode)
        if internal_code is not None:
            query = query.filter(Product.internal_code == internal_code)

        query = query.filter(Product.organization_uid_fk == organization_uid).order_by(Product.description.asc())

        page = _get_int_arg("page", 1)
        per_page = _get_int_arg("per_page", limit if limit is not None else 10)
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

        return jsonify({
            "items": items,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages
        })

    except Exception as e:
        import traceback
        print(f"Product list error: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@product_bp.route("/detail", methods=["GET"])
@firebase_auth_required
#@swag_from(product_docs["get_product"])
def detail_product():
    try:
        uid = _get_int_arg("uid", None)
        is_active = request.args.get("is_active")
        organization_uid = _get_int_arg("organization_uid", None)

        if organization_uid is None:
            return jsonify({"error": "Entity ID is required"}), 400
        if uid is None:
            return jsonify({"error": "ID is required"}), 400

        # Use filter(), not filter_by(), when passing expressions
        query = ProductDetail.query.filter(
            ProductDetail.product_id_fk == uid,
            ProductDetail.organization_uid_fk == organization_uid
        )

        if is_active is not None:
            is_active_val = 2 if str(is_active).lower() in ["true", "1"] else 1
            query = query.filter(ProductDetail.is_active == is_active_val)

        product_detail = query.first()

        if not product_detail:
            return jsonify({"error": "Product not found"}), 404

        return jsonify({
            "item": product_detail.to_dict() if hasattr(product_detail, "to_dict") else {},
        })

    except Exception as e:
        import traceback
        print(f"Product get error: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500