import traceback
from datetime import datetime, timezone
from flask import Blueprint, current_app, request, jsonify
from sqlalchemy import or_

from api_app.modules.utils.api_response import json_response, ApiResponse
from ..models.person_model import Person
from ..models.person_natural_model import PersonNatural
from ..models.phone_model import Phone
from ..models.mail_model import Mail
from ..models.address_model import Address  
from ..docs.person_natural import person_natural_docs
from main import db
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from .person_route import get_person

from api_app.modules.person.models import person_model

person_natural_bp = Blueprint("personnatural", __name__)

@person_natural_bp.route("/list", methods=["POST"])
@firebase_auth_required
@swag_from(person_natural_docs["list_person_natural"])
def list_person_natural():
    data = request.get_json()
    return get_person(data=data)

@person_natural_bp.route("/ui", methods=["POST"])
@firebase_auth_required
def upinsert_person_natural():
    try:
        data = request.get_json()
        current_app.logger.debug("Received person natural data:", data)

        _person_data = Person.from_json(data)
        _pn_data = PersonNatural.from_json(data)

        if (_person_data.main_organization_uid_fk is None or _person_data.main_organization_uid_fk == "") or (_person_data.name is None or _person_data.name == ""):
            return json_response(
                response="MISSING_FIELDS"
            )

        if not _person_data.uid:
            # This is a create operation, check for duplicates first
            existing = Person.query.filter_by(
                main_organization_uid_fk=_person_data.main_organization_uid_fk
            ).filter(
                or_(
                    Person.id_number == _person_data.id_number,
                    Person.name == _person_data.name
                )
            ).first()

            if existing:
                return json_response(
                    response=ApiResponse.DUPLICATE_ENTRY
                )

        _person = Person.query.filter_by(uid=_person_data.uid).first()
     
        if _person: # Update existing record
            _person.name = _person_data.name
            _person.id_number = _person_data.id_number
            _person.is_active = _person_data.is_active
            _person.is_supplier = _person_data.is_supplier
            _person.iso2alpha = _person_data.iso2alpha
            _person.updated_at = datetime.now(timezone.utc)
            persisted_person = _person
        else: # Create new record
            _person_data.created_at = datetime.now(timezone.utc)
            _person_data.updated_at = datetime.now(timezone.utc)

            db.session.add(_person_data)
            persisted_person = _person_data

        db.session.flush()  # Flush to get the person ID for FK

        _pn_data.person_uid_fk = persisted_person.uid

        _person_natural = PersonNatural.query.filter_by(person_uid_fk= _pn_data.person_uid_fk).first()

        if _person_natural:
             # Update the existing managed instance from the temporary data object
            _person_natural.update_from(_pn_data)
            persisted_pn = _person_natural 
        else:
            db.session.add(_pn_data)
            persisted_pn = _pn_data
        
        db.session.commit()

        return json_response(
            response=ApiResponse.UPINSERTED_SUCCESSFULLY,
            data={"person": persisted_person.to_dict(), "person_natural": persisted_pn.to_dict()}
        )

    except Exception as e:
        current_app.logger.debug("Error upinserting person natural:", e)
        current_app.logger.debug(traceback.format_exc())
        db.session.rollback()
        return json_response(response=ApiResponse.INTERNAL_ERROR)