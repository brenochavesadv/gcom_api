
from backend.apps.commerciall_api.main import db
from datetime import datetime, timezone
from backend.modules.utils.api_response import ApiResponse
from flask import current_app
from backend.modules.utils.api_response import json_response, ApiResponse
from ..models.person_legal_partner_model import PersonLegalPartner
import traceback
import uuid

# upisert person legal partner function to create or update a record
def partner_upsert_service(data=None, person_uid_fk=None, apply_commit=True): 

    try:
        current_app.logger.debug("Received person legal partner data: %s", data)

        _data = PersonLegalPartner.from_json(data)

        if (_data.person_uid_fk in (None,"")) and person_uid_fk is not None:
            _data.person_uid_fk = person_uid_fk

        if (_data.person_uid_fk is None or _data.person_uid_fk == "") or (_data.name is None or _data.name == ""):
            current_app.logger.debug("Missing required fields: person_uid_fk or partner_name")
            return json_response(
                response=ApiResponse.MISSING_FIELDS,
            )

        _selected = db.session.get(PersonLegalPartner, _data.uid)

        if _selected:
            _selected.is_active = _data.is_active
            _selected.name = _data.name
            _selected.id_number = _data.id_number
            _selected.share_percentage = _data.share_percentage
            _selected.iso2alpha = _data.iso2alpha
            _selected.age_group = _data.age_group
            _selected.qualification = _data.qualification
            _selected.partner_identifier_code = _data.partner_identifier_code
            _selected.representative_name = _data.representative_name
            _selected.representative_id_number = _data.representative_id_number
            _selected.representative_qualification = _data.representative_qualification
            _selected.admission_date = _data.admission_date
            _selected.created_at = _selected.created_at
            _selected.updated_at = datetime.now(timezone.utc)
            _selected.sync_status = "PENDING"
            response = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected

        else:
            _data.uid = str(uuid.uuid4())
            _data.created_at = datetime.now(timezone.utc)
            _data.updated_at = datetime.now(timezone.utc)
            _data.sync_status = "PENDING"
            db.session.add(_data)
            response = ApiResponse.CREATED_SUCCESSFULLY
            persisted = _data

        if apply_commit:
            db.session.commit()

        return json_response(
            response=response,
            data={"person_legal_partner": persisted.to_dict()}
        )

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
