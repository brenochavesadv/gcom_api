"""Product receipt API."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import wraps
import os

from flask import Blueprint, current_app, request
from sqlalchemy import and_, or_

from backend.apps.commerciall_api.main import db
from backend.modules.person.models.person_model import Person
from backend.modules.utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from ..models.product_detail_model import ProductDetail
from ..models.product_model import Product
from ..models.product_receipt_model import ProductReceipt, ProductReceiptItem
from ..models.product_supplier_model import ProductSupplier
from ..models.product_cfg_model import ProductCfg

product_receipt_bp = Blueprint("product_receipt", __name__)

_ZERO = Decimal("0")
_Q = Decimal("0.001")
_M = Decimal("0.01")


def _receipt_permission(permission):
    """Check Firebase custom claims after the authentication decorator runs."""
    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            user = getattr(request, "firebase_user", None)
            if user is None and os.getenv("FLASK_ENV", "production") != "production":
                return function(*args, **kwargs)
            permissions = user.get("permissions", []) if isinstance(user, dict) else []
            if permission not in permissions:
                return _error("FORBIDDEN", "Permission denied", ApiResponse.FORBIDDEN)
            return function(*args, **kwargs)
        return wrapped
    return decorator


def _receipt_read_permission(function):
    """Allow either receipt capability to read scoped receipt history."""
    @wraps(function)
    def wrapped(*args, **kwargs):
        user = getattr(request, "firebase_user", None)
        if user is None and os.getenv("FLASK_ENV", "production") != "production":
            return function(*args, **kwargs)
        permissions = user.get("permissions", []) if isinstance(user, dict) else []
        if not {"product.receipts.receive", "product.receipts.cancel"}.intersection(permissions):
            return _error("FORBIDDEN", "Permission denied", ApiResponse.FORBIDDEN)
        return function(*args, **kwargs)
    return wrapped


def _error(code, message, response=ApiResponse.VALIDATION_ERROR):
    return json_response(response=response, data={"code": code, "message": message})


def _decimal(value, scale, field):
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field} must be a decimal string")
    if not parsed.is_finite() or parsed < 0 or parsed.quantize(scale) != parsed:
        raise ValueError(f"{field} has invalid precision or value")
    return parsed


def _date(value, field, required=False):
    if value in (None, ""):
        if required:
            raise ValueError(f"{field} is required")
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError):
        raise ValueError(f"{field} must use YYYY-MM-DD")


def _org(payload):
    value = payload.get("organization_uid")
    main = payload.get("main_organization_uid")
    if value in (None, "") or main in (None, ""):
        raise ValueError("organization_uid and main_organization_uid are required")
    return int(value), int(main)


def _supplier(organization, main, uid):
    return Person.query.filter(
        Person.uid == int(uid),
        Person.main_organization_uid_fk == int(main),
        Person.is_active == 2,
        Person.is_supplier == 1,
    ).first()


def _line_json(item, product=None, detail=None):
    values = {
        "cost_method": "legacy",
        "tax_br": None,
        "acquisition_cost": None,
        "product_uid": str(item.product_uid_fk),
        "product_detail_uid": str(detail.uid) if detail else str(item.product_uid_fk),
        "version": detail.updated_at.isoformat() if detail and detail.updated_at else "",
        "fiscal_quantity": str(item.fiscal_quantity),
        "front_quantity": str(item.front_quantity),
        "storage_1_quantity": str(item.storage_1_quantity),
        "storage_2_quantity": str(item.storage_2_quantity),
        "storage_3_quantity": str(item.storage_3_quantity),
        "purchase_price": str(item.purchase_price),
        "freight": str(item.freight),
        "icms_percent": "0.00",
        "ipi_percent": str(item.ipi_percent),
        "markup": str(item.markup),
        "minimum_stock": str(detail.inventory_lowest_qty) if detail else "0.000",
        "sale_prices": [str(getattr(item, f"sale_price_{n}")) for n in range(1, 6)],
        "activate": bool(detail and detail.is_active == 2),
    }
    if product:
        values.update({"internal_code": str(product.internal_code), "description": product.description,
                       "barcode": product.barcode, "unit": str(product.unit_id_fk)})
    return values


def _lookup_product_json(product, detail, supplier_code=""):
    return {
        "cost_method": "legacy",
        "tax_br": None,
        "acquisition_cost": None,
        "product_uid": str(product.uid),
        "product_detail_uid": str(detail.uid),
        "version": detail.updated_at.isoformat() if detail.updated_at else "",
        "internal_code": str(product.internal_code),
        "unit": str(product.unit_id_fk),
        "description": product.description,
        "barcode": product.barcode or "",
        "supplier_code": supplier_code,
        "tax_rate_uid": str(detail.aliq or 0),
        "fiscal_quantity": "0.000",
        "front_quantity": "0.000",
        "storage_1_quantity": "0.000",
        "storage_2_quantity": "0.000",
        "storage_3_quantity": "0.000",
        "purchase_price": str(detail.purchase_price or 0),
        "freight": str(detail.shipping_price or 0),
        "icms_percent": "0.00",
        "ipi_percent": str(detail.ipi or 0),
        "markup": str(detail.profit or 0),
        "minimum_stock": str(detail.inventory_lowest_qty or 0),
        "sale_prices": [str(getattr(detail, f"sell_price_{n}") or 0) for n in range(1, 6)],
        "activate": detail.is_active == 2,
    }


@product_receipt_bp.post("/lookup/suppliers")
@firebase_auth_required
def lookup_receipt_suppliers():
    query = str(request.args.get("query", "")).strip()
    if len(query) < 1:
        return _error("VALIDATION_FAILED", "query is required")
    main = request.args.get("main_organization_uid")
    if not main:
        return _error("VALIDATION_FAILED", "main_organization_uid is required")
    rows = Person.query.filter(Person.main_organization_uid_fk == int(main), Person.is_active == 2,
                               Person.is_supplier == 1,
                               or_(Person.name.ilike(f"%{query}%"), Person.id_number == query)).limit(20).all()
    return json_response(ApiResponse.REQUEST_SUCCESSFUL, [{"uid": str(x.uid), "name": x.name, "tax_id": x.id_number} for x in rows])



@product_receipt_bp.post("/lookup/products")
@firebase_auth_required
def lookup_receipt_products():
    data = request.get_json(silent=True) or {}
    try:
        organization, main = _org(data)
        mode = data.get("mode")
        query = str(data.get("query", ""))
        if mode == "description" and len(query) < 3:
            raise ValueError("description queries require at least three characters")
        if mode not in {"description", "internalCode", "barcode", "supplierCode"}:
            raise ValueError("unsupported lookup mode")
        base = Product.query.join(ProductDetail, and_(ProductDetail.product_uid_fk == Product.uid,
              ProductDetail.organization_uid_fk == organization, ProductDetail.main_organization_uid_fk == main,
              ProductDetail.combo_product_uid == 0)).filter(Product.main_organization_uid_fk == main)
        if mode == "description": base = base.filter(Product.description.ilike(f"%{query}%"))
        elif mode == "internalCode": base = base.filter(Product.internal_code == int(query))
        elif mode == "barcode": base = base.filter(Product.barcode == query)
        else:
            base = base.join(ProductSupplier, ProductSupplier.product_uid_fk == Product.uid).filter(
                ProductSupplier.main_organization_uid_fk == main, ProductSupplier.product_supplier_code == query,
                ProductSupplier.person_uid_fk == int(data.get("supplier_uid")))
        rows = base.filter(Product.is_active == 2).limit(20).all()
        result = []
        for product in rows:
            detail = next((d for d in product.product_detail if d.organization_uid_fk == organization), None)
            if detail is None:
                continue
            mapping = None
            if data.get("supplier_uid"):
                mapping = ProductSupplier.query.filter_by(
                    main_organization_uid_fk=main,
                    product_uid_fk=product.uid,
                    person_uid_fk=int(data["supplier_uid"]),
                ).first()
            result.append({
                "uid": str(product.uid),
                "is_active": product.is_active == 2,
                "image_url": getattr(product, "image_url", "") or "",
                "defaults": _lookup_product_json(product, detail, mapping.product_supplier_code if mapping else ""),
            })
        return json_response(ApiResponse.REQUEST_SUCCESSFUL, result)
    except (ValueError, TypeError) as exc:
        return _error("VALIDATION_FAILED", str(exc))


def _receipt_data(receipt):
    lines = []
    for item in receipt.items:
        detail = ProductDetail.query.filter_by(
            product_uid_fk=item.product_uid_fk,
            organization_uid_fk=receipt.organization_uid_fk,
            combo_product_uid=0,
        ).first()
        product = Product.query.filter_by(uid=item.product_uid_fk).first()
        lines.append(_line_json(item, product, detail))
    return {"uid": str(receipt.uid), "code": str(receipt.code), "version": receipt.version,
            "organization_uid": str(receipt.organization_uid_fk), "supplier_name": receipt.supplier.name if receipt.supplier else None,
            "supplier_tax_id": receipt.supplier.id_number if receipt.supplier else None,
            "received_date": receipt.received_date.date().isoformat(), "order_number": receipt.order_number,
            "invoice_number": receipt.invoice_number, "status": receipt.status, "total": str(receipt.total),
            "lines": lines}


@product_receipt_bp.get("/")
@firebase_auth_required
@_receipt_read_permission
def list_product_receipts():
    """List receipts in the authenticated organization with bounded filters."""
    try:
        organization = request.args.get("organization_uid")
        if not organization:
            raise ValueError("organization_uid is required")
        organization = int(organization)
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", 20)), 1), 100)
        query = ProductReceipt.query.filter_by(organization_uid_fk=organization)
        start = _date(request.args.get("start_date"), "start_date")
        end = _date(request.args.get("end_date"), "end_date")
        if start:
            query = query.filter(ProductReceipt.received_date >= start)
        if end:
            query = query.filter(ProductReceipt.received_date < end.replace(hour=23, minute=59, second=59))
        supplier_uid = request.args.get("supplier_uid")
        if supplier_uid:
            query = query.filter(ProductReceipt.supplier_uid_fk == int(supplier_uid))
        product_uid = request.args.get("product_uid")
        if product_uid:
            query = query.join(ProductReceiptItem, ProductReceiptItem.receipt_uid_fk == ProductReceipt.uid).filter(
                ProductReceiptItem.product_uid_fk == int(product_uid)
            )
        result = query.order_by(ProductReceipt.received_date.desc(), ProductReceipt.uid.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return json_response(ApiResponse.REQUEST_SUCCESSFUL, {
            "items": [_receipt_data(row) for row in result.items],
            "page": result.page,
            "per_page": result.per_page,
            "pages": result.pages,
            "total": result.total,
        })
    except (ValueError, TypeError):
        return _error("VALIDATION_FAILED", "Invalid receipt list filters")


@product_receipt_bp.post("/")
@firebase_auth_required
@_receipt_permission("product.receipts.receive")
def receive_product_receipt():
    payload = request.get_json(silent=True) or {}
    try:
        organization, main = _org(payload)
        request_id = payload.get("request_id")
        if not request_id: raise ValueError("request_id is required")
        supplier = _supplier(organization, main, payload.get("supplier_uid"))
        if not supplier: return _error("INVALID_SUPPLIER", "Supplier is not active or in scope", ApiResponse.FORBIDDEN)
        lines = payload.get("lines")
        if not isinstance(lines, list) or not lines: raise ValueError("at least one line is required")
        received = _date(payload.get("received_date"), "received_date", True)
        order_date = _date(payload.get("order_date"), "order_date")
        invoice_date = _date(payload.get("invoice_date"), "invoice_date")
        if payload.get("generate_payable") is not False: raise ValueError("generate_payable must be false")
        if payload.get("replace_prices"):
            permissions = getattr(request, "firebase_user", {}) or {}
            if "product.receipts.change_prices" not in permissions.get("permissions", []):
                return _error("FORBIDDEN", "Price replacement permission is required", ApiResponse.FORBIDDEN)
        if len(str(payload.get("order_number", ""))) > 15 or len(str(payload.get("invoice_number", ""))) > 15: raise ValueError("document number is too long")
        if ProductReceipt.query.filter_by(organization_uid_fk=organization, actor_uid=str(request_id)).first():
            return json_response(ApiResponse.REQUEST_SUCCESSFUL, _receipt_data(ProductReceipt.query.filter_by(organization_uid_fk=organization, actor_uid=str(request_id)).first()))
        total = _ZERO; quantity = _ZERO; item_models = []
        seen = set()
        for line in lines:
            product_uid = int(line["product_uid"])
            if product_uid in seen: raise ValueError("duplicate product in receipt")
            seen.add(product_uid)
            detail = ProductDetail.query.filter_by(uid=int(line["product_detail_uid"]), product_uid_fk=product_uid,
                                                   organization_uid_fk=organization, main_organization_uid_fk=main).with_for_update().first()
            product = Product.query.filter_by(uid=product_uid, main_organization_uid_fk=main, is_active=2).first()
            if not product or not detail: return _error("STALE_PRODUCT", "Product detail is unavailable", ApiResponse.CONFLICT)
            fiscal = _decimal(line.get("fiscal_quantity", "0.000"), _Q, "fiscal_quantity")
            front = _decimal(line.get("front_quantity", "0.000"), _Q, "front_quantity")
            storage = _decimal(line.get("storage_1_quantity", "0.000"), _Q, "storage_1_quantity")
            purchase = _decimal(line.get("purchase_price", "0.00"), _M, "purchase_price")
            freight = _decimal(line.get("freight", "0.00"), _M, "freight")
            ipi = _decimal(line.get("ipi_percent", "0.00"), _M, "ipi_percent")
            markup = _decimal(line.get("markup", "0.00"), _M, "markup")
            prices = [_decimal(x, _M, "sale_price") for x in line.get("sale_prices", [])]
            if len(prices) != 5: raise ValueError("sale_prices must contain five values")
            physical = front + storage
            if physical <= 0: raise ValueError("physical quantity must be positive")
            cost = purchase + freight + (purchase * ipi / 100)
            if not payload.get("replace_prices"):
                registered = [detail.sell_price_1, detail.sell_price_2, detail.sell_price_3,
                              detail.sell_price_4, detail.sell_price_5]
                if (purchase != Decimal(str(detail.purchase_price or 0))
                        or freight != Decimal(str(detail.shipping_price or 0))
                        or markup != Decimal(str(detail.profit or 0))
                        or any(price != Decimal(str(old or 0)) for price, old in zip(prices, registered))):
                    return _error("FORBIDDEN", "Price replacement permission is required", ApiResponse.FORBIDDEN)
            total += cost * physical; quantity += fiscal
            detail.inventory_tax_qty = (detail.inventory_tax_qty or 0) + fiscal
            detail.inventory_front_qty = (detail.inventory_front_qty or 0) + front
            detail.inventory_storage_1_qty = (detail.inventory_storage_1_qty or 0) + storage
            detail.inventory_lowest_qty = _decimal(line.get("minimum_stock", "0.000"), _Q, "minimum_stock")
            detail.is_active = 2 if line.get("activate", True) else 1
            product.description = str(line.get("description", product.description))[:60]
            product.barcode = str(line.get("barcode", product.barcode or ""))[:25]
            product.supplier_person_uid_fk = supplier.uid
            supplier_code = line.get("supplier_code")
            if supplier_code is not None:
                mapping = ProductSupplier.query.filter_by(
                    main_organization_uid_fk=main, product_uid_fk=product_uid,
                    person_uid_fk=supplier.uid,
                ).first()
                if mapping is None:
                    mapping = ProductSupplier(main_organization_uid_fk=main, product_uid_fk=product_uid,
                                              person_uid_fk=supplier.uid)
                    db.session.add(mapping)
                mapping.product_supplier_code = str(supplier_code)
            if payload.get("replace_prices"):
                detail.purchase_price = purchase
                detail.shipping_price = freight
                detail.ipi = ipi
                detail.cost_price = cost
                detail.profit = markup
                for n, price in enumerate(prices, 1):
                    setattr(detail, f"sell_price_{n}", price)
            item_models.append(ProductReceiptItem(organization_uid_fk=organization, product_uid_fk=product_uid,
                fiscal_quantity=fiscal, front_quantity=front, storage_1_quantity=storage,
                storage_2_quantity=0, storage_3_quantity=0, cost_price=cost, tax_rate_uid_fk=None,
                purchase_price=purchase, freight=freight, ipi_percent=ipi, markup=markup,
                **{f"sale_price_{n}": prices[n-1] for n in range(1, 6)}))
        receipt = ProductReceipt(organization_uid_fk=organization, code=0, supplier_uid_fk=supplier.uid,
            received_date=received, total=total.quantize(_M), quantity=quantity, generate_payable=0,
            order_date=order_date, order_number=payload.get("order_number"), order_value=payload.get("order_value"),
            invoice_date=invoice_date, invoice_number=payload.get("invoice_number"), invoice_value=payload.get("invoice_value"),
            created_at=datetime.utcnow(), actor_uid=str(request_id), status_flag=1)
        db.session.add(receipt); db.session.flush()
        receipt.code = receipt.uid
        for item in item_models: item.receipt_uid_fk = receipt.uid; db.session.add(item)
        db.session.commit()
        return json_response(ApiResponse.CREATED_SUCCESSFULLY, _receipt_data(receipt))
    except (ValueError, KeyError, TypeError) as exc:
        db.session.rollback(); return _error("VALIDATION_FAILED", str(exc))
    except Exception:
        db.session.rollback(); current_app.logger.exception("Product receipt failed")
        raise


@product_receipt_bp.get("/<code>")
@firebase_auth_required
def find_product_receipt(code):
    organization = request.args.get("organization_uid")
    receipt = ProductReceipt.query.filter_by(code=code, organization_uid_fk=organization).first()
    if not receipt: return _error("RECEIPT_NOT_FOUND", "Receipt not found", ApiResponse.NOT_FOUND)
    return json_response(ApiResponse.REQUEST_SUCCESSFUL, _receipt_data(receipt))


@product_receipt_bp.post("/<int:uid>/cancel")
@firebase_auth_required
@_receipt_permission("product.receipts.cancel")
def cancel_product_receipt(uid):
    payload = request.get_json(silent=True) or {}
    try:
        organization, _ = _org(payload)
        if not payload.get("request_id"):
            raise ValueError("request_id is required")
        receipt = ProductReceipt.query.filter_by(uid=uid, organization_uid_fk=organization).with_for_update().first()
        if not receipt: return _error("RECEIPT_NOT_FOUND", "Receipt not found", ApiResponse.NOT_FOUND)
        if receipt.status != "posted": return _error("ALREADY_CANCELLED", "Receipt is already cancelled", ApiResponse.CONFLICT)
        if payload.get("version") and payload["version"] != receipt.version: return _error("STALE_RECEIPT", "Receipt changed", ApiResponse.CONFLICT)
        for item in receipt.items:
            detail = ProductDetail.query.filter_by(product_uid_fk=item.product_uid_fk, organization_uid_fk=organization,
                                                   combo_product_uid=0).with_for_update().first()
            if not detail: raise ValueError("affected product detail was not found")
            detail.inventory_tax_qty -= item.fiscal_quantity; detail.inventory_front_qty -= item.front_quantity
            detail.inventory_storage_1_qty -= item.storage_1_quantity; detail.inventory_storage_2_qty -= item.storage_2_quantity
            detail.inventory_storage_3_qty -= item.storage_3_quantity
        receipt.status_flag = 0; db.session.commit()
        return json_response(ApiResponse.REQUEST_SUCCESSFUL, _receipt_data(receipt))
    except (ValueError, TypeError) as exc:
        db.session.rollback(); return _error("VALIDATION_FAILED", str(exc))
    except Exception:
        db.session.rollback(); current_app.logger.exception("Product receipt cancellation failed")
        raise
