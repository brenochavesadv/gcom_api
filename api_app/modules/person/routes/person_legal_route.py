from main import db
from sqlalchemy import or_
from datetime import datetime, timezone
from flask import Blueprint, current_app, request
from api_app.modules.utils.api_response import json_response, ApiResponse, extract_data
from api_app.modules.person.routes.person_route import get_person
from ..models.person_model import Person
from ..models.person_legal_model import PersonLegal
from sqlalchemy.orm import selectinload
from ..services.address_services import upinsert_address
from ..services.mail_services import upinsert_mail
from ..services.phone_services import upinsert_phone
from ..services.person_legal_activity_services import upinsert_pl_activity
from ..services.person_legal_br_tax_regime_services import upinsert_pl_br_tax_regime
from ..services.person_legal_partner_services import upinsert_pl_partner
from ...auth_firebase.firebase_decorators import firebase_auth_required
import traceback

person_legal_bp = Blueprint("PersonLegal", __name__)


def _require_child_success(result, operation_name):
    response, status_code = result if isinstance(result, tuple) else (result, 500)
    if status_code >= 400:
        payload = response.get_json() if hasattr(response, "get_json") else {}
        message = payload.get("message") if isinstance(payload, dict) else "Unknown error"
        raise RuntimeError(f"{operation_name} failed: {message}")


def _has_meaningful_value(value):
    return value is not None and value != ""


def _should_process(item, required_field):
    return isinstance(item, dict) and _has_meaningful_value(item.get(required_field))

@person_legal_bp.route("/list", methods=["POST"])
@firebase_auth_required
#@swag_from(person_legal_docs["listselected_person_legal"])
def listselected_person_legal():
    data = request.get_json()
    return get_person(data=data)


@person_legal_bp.route("/ui", methods=["POST"])
@firebase_auth_required
def upinsertselected_person_legal():
    try:
        uad = request.args.get("uad", default=0, type=int)
        update_all_data = uad == 1  # True for 1: update all person legal data including partners, activities, tax regimes, etc.
        data = request.get_json()
        #current_app.logger.debug(f"Received person legal data: {data}")

        person_data = Person.from_json(data)
        plegal_data = PersonLegal.from_json(data)

        # Treat 0/empty UID as "new record" to avoid stale lookups using UID 0.
        if person_data.uid in (0, "0", ""):
            person_data.uid = None

        if (person_data.main_organization_uid_fk is None or person_data.main_organization_uid_fk == "") or (person_data.name is None or person_data.name == ""):
            return json_response(
                response="MISSING_FIELDS"
            )

        if not person_data.uid:
            # This is a create operation, check for duplicates first
            existing = Person.query.filter_by(
                main_organization_uid_fk=person_data.main_organization_uid_fk
            ).filter(
                or_(
                    Person.id_number == person_data.id_number,
                    Person.name == person_data.name
                )
            ).first()

            if existing:
                return json_response(
                    response=ApiResponse.DUPLICATE_ENTRY
                )

        # put a indentifier in the name if is not headquarter
        if person_data.name and plegal_data.is_headquarter != 1:
            person_data.name = f"{person_data.name} {person_data.id_number[8:12]}"

        selected_person = Person.query.filter_by(uid=person_data.uid).first() if person_data.uid else None
     
        if selected_person: # Update existing record
            selected_person.name = person_data.name
            selected_person.id_number = person_data.id_number
            selected_person.is_active = person_data.is_active
            selected_person.is_supplier = person_data.is_supplier
            selected_person.iso2alpha = person_data.iso2alpha
            selected_person.updated_at = datetime.now(timezone.utc)
            persisted_person = selected_person
            
        else: # Create new record
            person_data.created_at = datetime.now(timezone.utc)
            person_data.updated_at = datetime.now(timezone.utc)

            db.session.add(person_data)
            db.session.flush()  # Flush to get the generated person ID for FK
            if not person_data.uid:
                raise RuntimeError("Unable to generate a valid UID for person.")
            
            persisted_person = person_data

        person_uid = persisted_person.uid
        organization_uid = persisted_person.main_organization_uid_fk
        
        selected_person_legal = PersonLegal.query.filter_by(person_uid_fk=person_uid).first()

        if selected_person_legal:
            # Update the existing managed instance from the temporary data object
            selected_person_legal.updatable_fields(plegal_data)
        else:   
            plegal_data.person_uid_fk = person_uid
            db.session.add(plegal_data)

        if update_all_data:
            # Handle additional person legal data (partners, activities, tax regimes, etc.) here
            for address_data in data.get("addresses", []):
                upinsert_address(data=address_data, person_uid_fk=person_uid, auto_commit=False)
 
            for mail_data in data.get("mails", []):
                upinsert_mail(data=mail_data, person_uid_fk=person_uid, auto_commit=False)

            for phone_data in data.get("phones", []):
                upinsert_phone(data=phone_data, person_uid_fk=person_uid, auto_commit=False)

            for activity_data in data.get("activities", []):
                upinsert_pl_activity(data=activity_data, person_uid_fk=person_uid, auto_commit=False)

            for tax_regime_data in data.get("br_tax_regimes", []):
                upinsert_pl_br_tax_regime(data=tax_regime_data, person_uid_fk=person_uid, auto_commit=False)

            for partner_data in data.get("partners", []):
                upinsert_pl_partner(data=partner_data, person_uid_fk=person_uid, auto_commit=False)

        db.session.commit()

        response = get_person(data={"u": person_uid, "o": organization_uid, "t": "2", "ad": "1"})  # Refresh the person data after commit
        response_body = response[0].get_json() if isinstance(response, tuple) and hasattr(response[0], "get_json") else {}

        return response

    except Exception as e:
        current_app.logger.debug(f"Error upinserting person legal: {e}")
        current_app.logger.debug(traceback.format_exc())
        db.session.rollback()

    return json_response(response=ApiResponse.INTERNAL_ERROR)