import traceback
import uuid
from backend.apps.commerciall_api.main import db
from datetime import datetime, timezone
from datetime import date
from decimal import Decimal, InvalidOperation
from flask import Blueprint, current_app, request
from sqlalchemy import text

from backend.modules.utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from ..models.account_sections_model import AccountSection
from ..models.financial_account_model import FinancialAccount
from ..models.financial_movement_model import FinancialMovement
from ..models.financial_permission_model import FinancialPermission

financial_bp = Blueprint("financial", __name__)


def _payload():
    value = request.get_json(silent=True)
    return value if isinstance(value, dict) else {}


def _scope(data):
    claims = getattr(request, "firebase_user", None) or {}
    claim_main = claims.get("main_organization_uid", claims.get("mou"))
    claim_org = claims.get("organization_uid", claims.get("ou"))
    body_main = data.get("main_organization_uid", data.get("mou"))
    body_org = data.get("organization_uid", data.get("ou"))
    if claim_main not in (None, "") and body_main not in (None, "") and str(claim_main) != str(body_main):
        return None, None
    if claim_org not in (None, "") and body_org not in (None, "") and str(claim_org) != str(body_org):
        return None, None
    return claim_main or body_main, claim_org or body_org


def _error(code, message, status=422, fields=None):
    response, _ = json_response(response=ApiResponse.VALIDATION_ERROR,
                                 data={"error": {"code": code, "fields": fields or {}}, "message": message})
    response.status_code = status
    return response


def _money(value, allow_negative=True):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("invalid monetary value")
    if not allow_negative and result <= 0:
        raise ValueError("amount must be positive")
    if abs(result) > Decimal("9999999999.99") or result.as_tuple().exponent < -2:
        raise ValueError("invalid monetary precision")
    return result


def _date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError("date must use YYYY-MM-DD")


def _active_account(uid, main_org):
    return FinancialAccount.query.filter_by(uid=int(uid), main_organization_uid_fk=main_org).first()


@financial_bp.route("/context", methods=["POST"])
@firebase_auth_required
def financial_context():
    data = _payload()
    main_org, organization = _scope(data)
    if main_org in (None, "") or organization in (None, ""):
        return _error("MISSING_SCOPE", "main_organization_uid and organization_uid are required.", 400)
    accounts = FinancialAccount.query.filter_by(main_organization_uid_fk=main_org).order_by(FinancialAccount.name).all()
    sections = AccountSection.query.filter_by(main_organization_uid_fk=main_org, is_active=2, type=2).filter(
        AccountSection.category.in_([2, 5])
    ).order_by(AccountSection.description).all()
    return json_response(response=ApiResponse.REQUEST_SUCCESSFUL, data={
        "accounts": [account.to_dict() for account in accounts],
        "sections": {str(item.uid): f"{item.account_code} • {item.description}" for item in sections},
        "banks": {}, "currencies": {}, "document_species": {}, "users": {}, "permissions": [],
        "closed_before": None, "closing_version": "", "capabilities": {},
    })


@financial_bp.route("/accounts/save", methods=["POST"])
@financial_bp.route("/account/save", methods=["POST"])
@firebase_auth_required
def save_financial_account():
    data = _payload()
    main_org, organization = _scope(data)
    account_data = data.get("account", data)
    request_id = data.get("request_id")
    if not request_id or main_org in (None, "") or organization in (None, ""):
        return _error("MISSING_FIELDS", "request_id and organization scope are required.", 400)
    try:
        account = FinancialAccount.from_json(account_data, main_org)
        if not account.name or len(account.name) > 30 or account.section_uid in (None, ""):
            return _error("VALIDATION_FAILED", "name and an analytic section are required.")
        section = AccountSection.query.filter_by(uid=account.section_uid, main_organization_uid_fk=main_org).first()
        if section is None or section.type != 2 or section.category not in (2, 5) or section.is_active != 2:
            return _error("VALIDATION_FAILED", "section_uid must identify an active analytic section.")
        existing = FinancialAccount.query.filter_by(main_organization_uid_fk=main_org, name=account.name).first()
        if existing and existing.uid != account.uid:
            return _error("DUPLICATE_ACCOUNT_NAME", "Account name already exists.", 409)
        if account.type in (2, 3) and account.account_number:
            duplicate = FinancialAccount.query.filter_by(
                main_organization_uid_fk=main_org, account_number=account.account_number
            ).first()
            if duplicate and duplicate.uid != account.uid:
                return _error("DUPLICATE_ACCOUNT_NUMBER", "Account number already exists.", 409)
        if account.uid:
            persisted = _active_account(account.uid, main_org)
            if persisted is None:
                return json_response(response=ApiResponse.NOT_FOUND, data=None)
            if persisted.opening_balance != account.opening_balance:
                return _error("OPENING_BALANCE_IMMUTABLE", "Opening balance cannot be changed.", 409)
            for key, value in account.__dict__.items():
                if not key.startswith("_") and key not in {"uid", "main_organization_uid_fk", "opening_balance"}:
                    if hasattr(FinancialAccount, key):
                        setattr(persisted, key, value)
            account = persisted
        else:
            db.session.add(account)
            db.session.flush()
            db.session.add(FinancialMovement(
                organization_uid_fk=organization, account_uid=account.uid,
                section_uid=account.section_uid, direction=0,
                description=f"Saldo Inicial {account.name}", amount=account.opening_balance,
                date=account.opening_date, origin=0, user_uid=None, is_active=1,
            ))
        db.session.commit()
        return json_response(response=ApiResponse.SAVED_SUCCESSFULLY, data={"account": account.to_dict()})
    except (ValueError, InvalidOperation) as exc:
        db.session.rollback()
        return _error("VALIDATION_FAILED", str(exc))
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Financial account save failed")
        raise


@financial_bp.route("/movements/post", methods=["POST"])
@financial_bp.route("/post", methods=["POST"])
@firebase_auth_required
def post_financial_movement():
    data = _payload()
    main_org, organization = _scope(data)
    try:
        if not data.get("request_id") or main_org in (None, "") or organization in (None, ""):
            return _error("MISSING_FIELDS", "request_id and organization scope are required.", 400)
        movement_date = _date(data.get("date"))
        amount = _money(data.get("amount"), allow_negative=False)
        description = str(data.get("description", "")).strip()
        direction = data.get("direction")
        account = _active_account(data.get("account_uid"), main_org)
        destination = _active_account(data.get("destination_uid"), main_org) if data.get("destination_uid") else None
        if account is None or account.is_active != 1 or not description or len(description) > 50:
            return _error("VALIDATION_FAILED", "Active account and description are required.")
        if destination is not None and destination.uid == account.uid:
            return _error("VALIDATION_FAILED", "Transfer accounts must be distinct.")
        if direction not in ("credit", "debit"):
            return _error("VALIDATION_FAILED", "direction must be credit or debit.")
        first = FinancialMovement(
            organization_uid_fk=organization, account_uid=account.uid, section_uid=account.section_uid,
            direction=1 if direction == "credit" else 2, description=description[:50], amount=amount,
            date=movement_date, origin=1 if destination else 2, user_uid=None, is_active=1,
        )
        db.session.add(first)
        db.session.flush()
        if destination is not None:
            second = FinancialMovement(
                organization_uid_fk=organization, account_uid=destination.uid, section_uid=destination.section_uid,
                direction=2 if direction == "credit" else 1, description=description[:50], amount=amount,
                date=movement_date, origin=1, linked_uid=first.uid, user_uid=None, is_active=1,
            )
            db.session.add(second)
            db.session.flush()
            first.linked_uid = second.uid
            second.linked_uid = first.uid
        db.session.commit()
        return json_response(response=ApiResponse.SAVED_SUCCESSFULLY, data={"uid": str(first.uid)})
    except (ValueError, InvalidOperation) as exc:
        db.session.rollback()
        return _error("VALIDATION_FAILED", str(exc))
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Financial movement post failed")
        raise


@financial_bp.route("/statement", methods=["POST"])
@financial_bp.route("/movements/statement", methods=["POST"])
@firebase_auth_required
def financial_statement():
    data = _payload()
    main_org, organization = _scope(data)
    try:
        account = _active_account(data.get("account_uid"), main_org)
        if account is None:
            return json_response(response=ApiResponse.NOT_FOUND, data=None)
        query = FinancialMovement.query.filter_by(account_uid=account.uid, organization_uid_fk=organization, is_active=1)
        if data.get("from"):
            query = query.filter(FinancialMovement.date >= _date(data["from"]))
        if data.get("to"):
            query = query.filter(FinancialMovement.date <= _date(data["to"]))
        if data.get("description"):
            query = query.filter(FinancialMovement.description.ilike(f"%{data['description']}%"))
        if data.get("amount") is not None:
            query = query.filter(FinancialMovement.amount == _money(data["amount"]))
        all_rows = query.order_by(FinancialMovement.date.asc(), FinancialMovement.uid.asc()).all()
        balance = Decimal("0")
        items = []
        for row in all_rows:
            balance += row.amount if row.direction != 2 else -row.amount
            items.append((row, balance))
        page = max(int(data.get("page", 1)), 1)
        start, end = (page - 1) * 50, page * 50
        return json_response(response=ApiResponse.REQUEST_SUCCESSFUL, data={
            "items": [row.to_dict(current, str(row.uid)) for row, current in items[start:end]],
            "has_more": end < len(items),
        })
    except (ValueError, InvalidOperation) as exc:
        return _error("VALIDATION_FAILED", str(exc))


def _require_request_id(data):
    if not isinstance(data.get("request_id"), str) or not data["request_id"].strip():
        return _error("MISSING_FIELDS", "request_id is required.", 400)
    return None


def _movement_for_scope(data):
    main_org, organization = _scope(data)
    if main_org in (None, "") or organization in (None, ""):
        return None, _error("MISSING_SCOPE", "organization scope is required.", 400)
    try:
        movement = FinancialMovement.query.filter_by(
            uid=int(data.get("movement_uid", data.get("uid"))),
            organization_uid_fk=organization,
        ).first()
    except (TypeError, ValueError):
        movement = None
    if movement is None:
        return None, json_response(response=ApiResponse.NOT_FOUND, data=None)
    if data.get("version") not in (None, "", str(movement.uid)):
        return None, _error("STALE_VERSION", "Movement has changed.", 409)
    if _active_account(movement.account_uid, main_org) is None:
        return None, _error("FORBIDDEN", "Movement is outside the organization scope.", 403)
    return movement, None


@financial_bp.route("/movements/change-date", methods=["POST"])
@firebase_auth_required
def change_financial_movement_date():
    data = _payload()
    missing = _require_request_id(data)
    if missing:
        return missing
    movement, error = _movement_for_scope(data)
    if error:
        return error
    if movement.origin == 0:
        return _error("INVALID_ORIGIN", "Opening movements cannot be changed.", 409)
    try:
        new_date = _date(data.get("date"))
        movement.date = new_date
        if movement.origin == 1 and movement.linked_uid:
            linked = FinancialMovement.query.filter_by(uid=movement.linked_uid).first()
            if linked is not None:
                linked.date = new_date
        db.session.commit()
        return json_response(response=ApiResponse.UPDATED_SUCCESSFULLY, data={"uid": str(movement.uid)})
    except ValueError as exc:
        db.session.rollback()
        return _error("VALIDATION_FAILED", str(exc))
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Financial movement date change failed")
        raise


@financial_bp.route("/movements/void", methods=["POST"])
@firebase_auth_required
def void_financial_movement():
    data = _payload()
    missing = _require_request_id(data)
    if missing:
        return missing
    movement, error = _movement_for_scope(data)
    if error:
        return error
    if movement.origin not in (1, 2):
        return _error("INVALID_ORIGIN", "Only manual and transfer movements can be voided.", 409)
    movement.is_active = 2
    if movement.origin == 1 and movement.linked_uid:
        linked = FinancialMovement.query.filter_by(uid=movement.linked_uid).first()
        if linked is not None:
            linked.is_active = 2
    try:
        db.session.commit()
        return json_response(response=ApiResponse.UPDATED_SUCCESSFULLY, data={"uid": str(movement.uid)})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Financial movement void failed")
        raise


@financial_bp.route("/close", methods=["POST"])
@firebase_auth_required
def close_financial_period():
    data = _payload()
    missing = _require_request_id(data)
    if missing:
        return missing
    _, organization = _scope(data)
    if organization in (None, ""):
        return _error("MISSING_SCOPE", "organization_uid is required.", 400)
    try:
        closing_date = _date(data.get("date"))
        current = db.session.execute(
            text("SELECT cfg6 FROM configs WHERE id = :organization_uid FOR UPDATE"),
            {"organization_uid": organization},
        ).scalar_one_or_none()
        current_version = str(current or "")
        if data.get("version") not in (None, "", current_version):
            return _error("STALE_VERSION", "Closing date has changed.", 409)
        result = db.session.execute(
            text("UPDATE configs SET cfg6 = :closing_date WHERE id = :organization_uid"),
            {"closing_date": closing_date.isoformat(), "organization_uid": organization},
        )
        if result.rowcount == 0:
            db.session.rollback()
            return json_response(response=ApiResponse.NOT_FOUND, data=None)
        db.session.commit()
        return json_response(response=ApiResponse.UPDATED_SUCCESSFULLY, data={
            "closed_before": closing_date.isoformat(), "closing_version": closing_date.isoformat(),
        })
    except ValueError as exc:
        db.session.rollback()
        return _error("VALIDATION_FAILED", str(exc))
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Financial closing failed")
        raise


@financial_bp.route("/permissions", methods=["POST"])
@firebase_auth_required
def financial_permissions():
    data = _payload()
    _, organization = _scope(data)
    if organization in (None, "") or data.get("user_uid") in (None, ""):
        return _error("MISSING_FIELDS", "organization_uid and user_uid are required.", 400)
    permissions = FinancialPermission.query.join(
        FinancialAccount, FinancialAccount.uid == FinancialPermission.account_uid
    ).filter(
        FinancialPermission.user_uid == data["user_uid"],
        FinancialAccount.main_organization_uid_fk == data.get("main_organization_uid", data.get("mou")),
    ).all()
    return json_response(response=ApiResponse.REQUEST_SUCCESSFUL, data={
        "permissions": [permission.to_dict() for permission in permissions], "version": "",
    })


@financial_bp.route("/permissions/save", methods=["POST"])
@firebase_auth_required
def save_financial_permissions():
    data = _payload()
    missing = _require_request_id(data)
    if missing:
        return missing
    main_org, organization = _scope(data)
    user_uid, grants = data.get("user_uid"), data.get("permissions")
    if main_org in (None, "") or organization in (None, "") or user_uid in (None, "") or not isinstance(grants, list):
        return _error("MISSING_FIELDS", "organization scope, user_uid and permissions are required.", 400)
    try:
        account_ids = {int(grant["account_uid"]) for grant in grants if isinstance(grant, dict)}
        valid_ids = {account.uid for account in FinancialAccount.query.filter(
            FinancialAccount.main_organization_uid_fk == main_org, FinancialAccount.uid.in_(account_ids)
        ).all()}
        if account_ids != valid_ids:
            return _error("FORBIDDEN", "One or more accounts are outside the organization scope.", 403)
        FinancialPermission.query.filter(FinancialPermission.user_uid == user_uid).filter(
            FinancialPermission.account_uid.in_(valid_ids)
        ).delete(synchronize_session=False)
        for grant in grants:
            db.session.add(FinancialPermission(
                account_uid=int(grant["account_uid"]), user_uid=user_uid,
                movements=2 if grant.get("movements", False) else 1,
                payables=2 if grant.get("payables", False) else 1,
                transfers=2 if grant.get("transfers", False) else 1,
            ))
        db.session.commit()
        return json_response(response=ApiResponse.SAVED_SUCCESSFULLY, data={"permissions": grants, "version": ""})
    except (KeyError, TypeError, ValueError):
        db.session.rollback()
        return _error("VALIDATION_FAILED", "Invalid permission payload.")
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Financial permissions save failed")
        raise

@financial_bp.route("/l", methods=["POST"])
@firebase_auth_required
#@swag_from(product_docs["list_product"])
def list_unit():
    try:
        data = request.get_json() or {}

        uid = data.get("u")
        main_organization_uid_fk = data.get("mou")
        is_active = data.get("ia")
        is_section = data.get("is")
        type = data.get("t")
        category = data.get("c")
        reduced_code = data.get("rc")

        if main_organization_uid_fk not in (None, ""):
            query = AccountSection.query.filter(AccountSection.main_organization_uid_fk == main_organization_uid_fk)
        else:
            json_response(
                response=ApiResponse.MISSING_FIELDS,
                data={"error": "organization_uid_fk is required"}
            ), 400
       
        query = AccountSection.query.filter(AccountSection.main_organization_uid_fk == main_organization_uid_fk)

        if uid not in (None, ""):
            query = query.filter(AccountSection.uid == uid)
        if is_active not in (None, ""):
            query = query.filter(AccountSection.is_active == is_active)
        if is_section in (1, "1", "true", True):
            query = query.filter(AccountSection.is_section == 1)
        if type not in (None, ""):
            query = query.filter(AccountSection.type == type)
        if category not in (None, ""):
            query = query.filter(AccountSection.category == category)
        if reduced_code in (1, "1", "true", True):
            query = query.filter(AccountSection.reduced_code == reduced_code)

        result = query.order_by(AccountSection.account_code.asc()).all()

        accounts_list = []
        for item in result:
            accounts_list.append(item.to_dict())

        #print(f"Unit data: {units}")  # Debugging line to print the query results

        return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = {"accounts_list": accounts_list}
                )

    except Exception as e:
        import traceback
        current_app.logger.debug(f"Account Section list error: {traceback.format_exc()}")
        raise


@financial_bp.route("/ui", methods=["POST"])
@firebase_auth_required
def upsert_account_section():
    try:
        data = request.get_json()
        print (f"Received data for upsert account section: {data}")

        account = AccountSection.from_json(data) 

        if (account.main_organization_uid_fk in (None, "") or account.account_code in (None, "") or account.description in (None, "")):
            current_app.logger.debug("Missing required fields: organization_uid_fk, account_code or description")
            return json_response(
                response=ApiResponse.MISSING_FIELDS,
                data={"error": "main_organization_uid_fk, account_code and description are required"}
            )



        _selected = AccountSection.query.filter_by(uid=account.uid, main_organization_uid_fk=account.main_organization_uid_fk).first()

        if _selected:
            _selected.account_code = account.account_code
            _selected.is_active = account.is_active
            _selected.is_section = account.is_section
            _selected.description = account.description
            _selected.type = account.type
            _selected.category = account.category
            _selected.reduced_code = account.reduced_code
            _selected.updated_at = datetime.now(timezone.utc)
            _selected.sync_status = "PENDING"
            
            message = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
            
        else:
            account.uid = str(uuid.uuid4())
            account.updated_at = datetime.now(timezone.utc)
            account.created_at = datetime.now(timezone.utc)
            account.sync_status = "PENDING"
            db.session.add(account)
            message = ApiResponse.CREATED_SUCCESSFULLY
            persisted = account

        db.session.commit()

        return json_response(
            response=message,
            data={"account_section": persisted.to_dict()}
        )

    except Exception as e:
        current_app.logger.debug("Error creating/updating brand:", e)
        current_app.logger.debug(traceback.format_exc())
        db.session.rollback()
        raise
