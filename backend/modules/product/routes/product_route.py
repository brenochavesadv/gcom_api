from datetime import datetime, timezone
from uuid import uuid4
from flask import Blueprint, current_app, request

from backend.apps.commerciall_api.main import db
from backend.modules.utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from sqlalchemy.orm import joinedload, selectinload
from ..models.product_model import Product
from ..models.product_detail_model import ProductDetail
from ..models.product_supplier_model import ProductSupplier
from ..models.product_combo_model import ProductCombo
from ..models.product_combo_item_model import ProductComboItem
from ..models.product_cfg_model import ProductCfg
from ..tax_br.models.tax_br_model import TaxBr

product_bp = Blueprint("product", __name__)


_REGISTRATION_REQUIRED = ("product", "product_detail", "suppliers", "combo_items")
_STOCK_FIELDS = {
    "inventory_tax_qty",
    "inventory_front_qty",
    "inventory_storage_1_qty",
    "inventory_storage_2_qty",
    "inventory_storage_3_qty",
}


def _as_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value in (1, "1", "true", "True", "TRUE")


def _as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _registration_error(message, code="VALIDATION_ERROR"):
    return json_response(
        response=getattr(ApiResponse, code),
        data={"code": code, "message": message},
    )


def _product_values(payload):
    allowed = {
        "is_active", "internal_code", "barcode", "description", "short_description",
        "unit_id_fk", "product_category_uid_fk", "product_category_lv1_uid",
        "product_category_lv2_uid", "size", "width", "height", "cubage", "weight",
        "product_brand_uid_fk", "supplier_person_uid_fk", "additional_info",
        "allow_fractional_quantity", "is_own_production", "is_combo", "has_expiry", "image", "image_bytes",
    }
    values = {key: value for key, value in payload.items() if key in allowed}
    boolean_fields = ("is_active", "allow_fractional_quantity", "is_own_production", "is_combo", "has_expiry")
    for field in boolean_fields:
        if field in values:
            values[field] = int(_as_bool(values[field]))
    values.pop("uid", None)
    values.pop("created_at", None)
    values.pop("updated_at", None)
    # Organization scope is determined from the detail/authenticated request.
    values.pop("main_organization_uid_fk", None)
    return values


def _detail_values(payload):
    values = dict(payload)
    for field in ("is_active", "inventory_reduce_on_sell", "is_for_rental", "is_wholesale"):
        if field in values:
            values[field] = int(_as_bool(values[field]))
    # The registration contract must never overwrite balances.
    values = {key: value for key, value in values.items() if key not in _STOCK_FIELDS}
    values.pop("uid", None)
    values.pop("product_uid_fk", None)
    values.pop("created_at", None)
    values.pop("updated_at", None)
    return values


def _supplier_values(payload):
    return {
        "main_organization_uid_fk": payload.get(
            "organization_uid_fk", payload.get("main_organization_uid_fk")
        ),
        "person_uid_fk": payload.get("person_uid_fk"),
        "product_supplier_code": payload.get(
            "supplier_internal_code", payload.get("product_supplier_code")
        ),
    }


@product_bp.route("/register", methods=["POST"])
@firebase_auth_required
def register_product():
    """Create or update a product and its selected organization detail atomically."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _registration_error("A JSON object is required.", "BAD_REQUEST")

    missing = [key for key in _REGISTRATION_REQUIRED if key not in payload]
    if missing:
        return _registration_error(
            "Missing required fields: " + ", ".join(missing), "MISSING_FIELDS"
        )

    product_data = payload["product"]
    detail_data = payload["product_detail"]
    suppliers = payload["suppliers"]
    combo_items = payload["combo_items"]
    if not isinstance(product_data, dict) or not isinstance(detail_data, dict):
        return _registration_error("product and product_detail must be objects.")
    if not isinstance(suppliers, list) or not isinstance(combo_items, list):
        return _registration_error("suppliers and combo_items must be lists.")

    description = str(product_data.get("description", "")).strip()
    short_description = str(product_data.get("short_description", "")).strip()
    barcode = str(product_data.get("barcode", "")).strip()
    if not description or not short_description:
        return _registration_error("description and short_description are required.")
    if not barcode and not _as_bool(payload.get("generate_barcode")):
        return _registration_error("barcode is required unless generate_barcode is true.")

    organization_uid = detail_data.get("organization_uid_fk")
    main_organization_uid = detail_data.get("main_organization_uid_fk")
    if organization_uid in (None, "", "0") or main_organization_uid in (None, "", "0"):
        return _registration_error("product_detail organization identifiers are required.")

    product_uid = product_data.get("uid")
    existing = None
    if product_uid not in (None, "", "0", 0):
        existing = Product.query.get(_as_int(product_uid))
        if existing is None:
            return json_response(response=ApiResponse.NOT_FOUND, data={"code": "PRODUCT_NOT_FOUND"})

    try:
        query = Product.query.filter(Product.main_organization_uid_fk == main_organization_uid)
        query = query.filter(Product.description == description)
        if existing is not None:
            query = query.filter(Product.uid != existing.uid)
        if query.first() is not None:
            return _registration_error("description already exists.", "DUPLICATE_ENTRY")

        barcode_query = Product.query.filter(Product.main_organization_uid_fk == main_organization_uid)
        barcode_query = barcode_query.filter(Product.barcode == barcode)
        if existing is not None:
            barcode_query = barcode_query.filter(Product.uid != existing.uid)
        if barcode and barcode_query.first() is not None:
            return _registration_error("barcode already exists.", "DUPLICATE_ENTRY")

        if existing is None:
            product = Product(
                **_product_values(product_data),
                main_organization_uid_fk=main_organization_uid,
            )
            db.session.add(product)
            db.session.flush()
        else:
            product = existing
            if bool(product.is_combo) != _as_bool(product_data.get("is_combo")):
                return _registration_error("combo type cannot be changed.", "CONFLICT")
            for key, value in _product_values(product_data).items():
                if hasattr(Product, key):
                    setattr(product, key, value)

        detail = ProductDetail.query.filter_by(
            product_uid_fk=product.uid,
            organization_uid_fk=organization_uid,
        ).first()
        detail_values = _detail_values(detail_data)
        if detail is None:
            detail = ProductDetail(
                **detail_values,
                product_uid_fk=product.uid,
                organization_uid_fk=organization_uid,
                main_organization_uid_fk=main_organization_uid,
                internal_code=product.internal_code,
            )
            db.session.add(detail)
        else:
            for key, value in detail_values.items():
                if hasattr(ProductDetail, key):
                    setattr(detail, key, value)

        db.session.flush()
        for supplier in suppliers:
            if not isinstance(supplier, dict) or supplier.get("person_uid_fk") in (None, "", "0"):
                return _registration_error("Each supplier requires person_uid_fk.")
        person_ids = [str(item["person_uid_fk"]) for item in suppliers]
        if len(person_ids) != len(set(person_ids)):
            return _registration_error("Duplicate supplier references are not allowed.")

        ProductSupplier.query.filter_by(
            product_uid_fk=product.uid,
            main_organization_uid_fk=main_organization_uid,
        ).delete(synchronize_session=False)
        for supplier in suppliers:
            db.session.add(ProductSupplier(
                **_supplier_values(supplier),
                product_uid_fk=product.uid,
            ))

        tax_data = payload.get("tax_br")
        if tax_data is not None:
            if not isinstance(tax_data, dict):
                return _registration_error("tax_br must be an object.")
            tax_organization = tax_data.get(
                "organization_uid_fk", tax_data.get("organizationUidFk", organization_uid)
            )
            tax = TaxBr.query.filter_by(
                product_uid_fk=str(product.uid), organization_uid_fk=str(tax_organization)
            ).first()
            if tax is None:
                tax = TaxBr(
                    uid=str(tax_data.get("uid", "0"))
                    if tax_data.get("uid", "0") not in (None, "", "0")
                    else str(uuid4()),
                    product_uid_fk=str(product.uid),
                    organization_uid_fk=str(tax_organization),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                db.session.add(tax)
            tax_fields = {
                "uid": "uid",
                "ncm": "ncm",
                "cst": "cst",
                "cred_presumido": "cred_presumido",
                "credPresumido": "cred_presumido",
                "icms_pis_cofins_group_uid_fk": "icms_pis_cofins_group_uid_fk",
                "ibs_cbs_uid_fk": "ibs_cbs_uid_fk",
                "sync_status": "sync_status",
                "syncStatus": "sync_status",
            }
            for source, target in tax_fields.items():
                if source in tax_data and target != "uid":
                    setattr(tax, target, tax_data[source])
            tax.updated_at = datetime.now(timezone.utc)

        if combo_items and not bool(product.is_combo):
            return _registration_error("Only combo products may contain combo_items.", "CONFLICT")
        combo = ProductCombo.query.filter_by(
            product_uid_fk=product.uid,
            organization_uid_fk=organization_uid,
        ).first()
        if combo_items:
            if combo is None:
                combo = ProductCombo(
                    product_uid_fk=product.uid,
                    organization_uid_fk=organization_uid,
                )
                db.session.add(combo)
                db.session.flush()
            combo.items.clear()
            seen_component_ids = set()
            for item in combo_items:
                if not isinstance(item, dict):
                    return _registration_error("Each combo item must be an object.")
                component_uid = _as_int(item.get("product_uid_fk"))
                quantity = item.get("quantity")
                unit_price = item.get("unit_price")
                if component_uid <= 0 or component_uid == product.uid:
                    return _registration_error("Each combo item requires a valid component product.")
                if component_uid in seen_component_ids:
                    return _registration_error("Duplicate combo components are not allowed.")
                try:
                    if float(quantity) <= 0 or float(unit_price) < 0:
                        raise ValueError
                except (TypeError, ValueError):
                    return _registration_error("Combo quantity must be positive and unit_price non-negative.")
                component = Product.query.get(component_uid)
                if component is None:
                    return _registration_error("Combo component product was not found.", "NOT_FOUND")
                seen_component_ids.add(component_uid)
                combo.items.append(ProductComboItem(
                    product_uid_fk=component.uid,
                    quantity=quantity,
                    unit_price=unit_price,
                ))
        elif combo is not None:
            combo.items.clear()

        db.session.commit()
        product.product_detail = [detail]
        result = product.to_dict()
        result["product_detail"] = detail.to_dict()
        result["combo_items"] = [item.to_dict() for item in combo.items] if combo else []
        return json_response(response=ApiResponse.SAVED_SUCCESSFULLY, data={"product": result})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Product registration failed")
        raise

@product_bp.route("/l", methods=["POST"])
@firebase_auth_required
#@swag_from(product_docs["list_product"])
def list_product():
    try:
        data = request.get_json() or {}
        print (f"Received request data: {data}")  # Debugging line to print the request data
        uid = data.get("u")
        description = data.get("d")
        is_active = data.get("ia")
        is_combo = data.get("icb")
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
            
        query = query.filter(Product.main_organization_uid_fk == organization_uid).order_by(getattr(Product, order_by).asc())

        if count_table:
            query = query.options(selectinload(Product.product_count))

        if sale_tables:
            query = query.options(selectinload(Product.product_brand))
            query = query.options(selectinload(Product.product_detail))
            query = query.options(selectinload(Product.product_category))
            #query = query.options(selectinload(Product.product_inventory))
            query = query.options(selectinload(Product.product_tax_br))
            query = query.options(selectinload(Product.product_unit))
            
        if complementary_tables:                        
            query = query.options(selectinload(Product.product_expiry))
            query = query.options(selectinload(Product.product_supplier))
            
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        print(f" Query executed: {query}")  # Debugging line to print the executed query

        data_items = []
        for product in pagination.items:
                data_items.append({'product': product.to_dict()})

        print(f"Product data: {data_items}")  # Debugging line to print the query

        return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = data_items,
                    total = pagination.total,
                    page = pagination.page,
                    pages = pagination.pages
                )

    except Exception as e:
        import traceback
        current_app.logger.debug(f"Product list error: {traceback.format_exc()}")
        raise

@product_bp.route("/get_cfg", methods=["GET"])
@firebase_auth_required
def get_product_configs():
    organization_uid = request.args.get("ou")
    print(f"Received organization_uid: {organization_uid}")  # Debugging line to print the received organization_uid
    try:
        if organization_uid in (None, ""):
            return json_response(response="MISSING_FIELDS")

        _selected = ProductCfg.query.filter(ProductCfg.organization_uid_fk == organization_uid)

        if _selected.first() is None:
            return json_response(response="NOT_FOUND", data={"message": "Product configuration not found."})

        return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = _selected.first().to_dict(),
        )
    except Exception as e:
        import traceback
        current_app.logger.debug(f"ProductCfg list error: {traceback.format_exc()}")
        raise

@product_bp.route("/update_cfg", methods=["POST", "PUT"])
@firebase_auth_required
def update_product_configs():
    try:
        data = request.get_json(silent=True)
        print(f"Received request data for update_cfg: {data}")  # Debugging line to print the request data

        if not isinstance(data, dict):
            return json_response(
                response=ApiResponse.BAD_REQUEST,
                data={"code": "INVALID_JSON", "message": "Request body must be a JSON object."},
            )

        payload = data.get("product_cfg", data)
        if not isinstance(payload, dict):
            return json_response(
                response=ApiResponse.BAD_REQUEST,
                data={"code": "INVALID_PRODUCT_CONFIG", "message": "product_cfg must be a JSON object."},
            )

        cfg = ProductCfg.from_json(payload)
        
        if cfg.organization_uid_fk in (None, ""):
            return json_response(response="MISSING_FIELDS")
        
        config_query = ProductCfg.query.filter_by(
            organization_uid_fk=cfg.organization_uid_fk,
        )
        if getattr(cfg, "uid", None) not in (None, "", "0"):
            config_query = config_query.filter_by(uid=cfg.uid)
        _selected = config_query.first()

        if _selected is None:
            return json_response(response="NOT_FOUND", data={"message": "Product configuration not found for update."})

        fields = (
            "allow_change_price_during_sale", "default_profit",
            "title_price_1", "title_price_2", "title_price_3", "title_price_4", "title_price_5",
            "type_percent_over_price_1", "percent_to_price_2", "percent_to_price_3", "percent_to_price_4", "percent_to_price_5",
            "commission_over_price_1", "commission_over_price_2", "commission_over_price_3", "commission_over_price_4", "commission_over_price_5",
            "max_discount_over_price_1", "max_discount_over_price_2", "max_discount_over_price_3", "max_discount_over_price_4", "max_discount_over_price_5",
        )
        for field in fields:
            if hasattr(cfg, field):
                setattr(_selected, field, getattr(cfg, field))

        _selected.updated_at = datetime.now(timezone.utc)
        _selected.sync_status = "PENDING"
        
        db.session.commit()


        return json_response(
                    response = ApiResponse.SAVED_SUCCESSFULLY,
            data = {"product_cfg": _selected.to_dict()},
        )
        
    except Exception as e:
        import traceback
        current_app.logger.debug(f"ProductCfg save error: {traceback.format_exc()}")
        raise
