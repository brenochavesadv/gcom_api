
from main import db
from datetime import datetime
from api_app.modules.utils.api_response import ApiResponse
from flask import current_app
from api_app.modules.utils.api_response import json_response, ApiResponse
from ..models.person_legal_partner_model import PersonLegalPartner
import traceback
import uuid

# upisert person legal partner function to create or update a record
def upinsert_pl_partner(data=None, person_uid_fk=None, auto_commit=True): 

    try:
        current_app.logger.debug("Received person legal partner data: %s", data)

        partner_data = PersonLegalPartner.from_json(data)

        if (partner_data.person_uid_fk in (None,"")) and person_uid_fk is not None:
            partner_data.person_uid_fk = person_uid_fk

        if (partner_data.person_uid_fk is None or partner_data.person_uid_fk == "") or (partner_data.name is None or partner_data.name == ""):
            current_app.logger.debug("Missing required fields: person_uid_fk or partner_name")
            return json_response(
                response=ApiResponse.MISSING_FIELDS,
            )

        _selected = PersonLegalPartner.query.filter_by(uid=partner_data.uid).first() if partner_data.uid else None
        if not _selected:
            _selected = PersonLegalPartner.query.filter_by(person_uid_fk=partner_data.person_uid_fk, name=partner_data.name).first() if partner_data.person_uid_fk and partner_data.name else None

        if _selected:
            _selected.is_active = partner_data.is_active
            _selected.name = partner_data.name
            _selected.id_number = partner_data.id_number
            _selected.share_percentage = partner_data.share_percentage
            _selected.iso2alpha = partner_data.iso2alpha
            _selected.age_group = partner_data.age_group
            _selected.qualification = partner_data.qualification
            _selected.partner_identifier_code = partner_data.partner_identifier_code
            _selected.representative_name = partner_data.representative_name
            _selected.representative_id_number = partner_data.representative_id_number
            _selected.representative_qualification = partner_data.representative_qualification
            _selected.admission_date = partner_data.admission_date
            _selected.sync_status = partner_data.sync_status
            _selected.updated_at = datetime.now()
            response = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected

        else:
            partner_data.uid = str(uuid.uuid4())
            partner_data.created_at = datetime.now()
            partner_data.updated_at = datetime.now()
            db.session.add(partner_data)
            response = ApiResponse.CREATED_SUCCESSFULLY
            persisted = partner_data

        if auto_commit:
            db.session.commit()
        else:
            db.session.flush()

        return json_response(
            response=response,
            data={"person_legal_partner": persisted.to_dict()}
        )

    except Exception as e:
        current_app.logger.debug("Error creating/updating person legal partner: %s", e)
        current_app.logger.debug(traceback.format_exc())
        if auto_commit:
            db.session.rollback()
            return json_response(response=ApiResponse.INTERNAL_ERROR)
        raise