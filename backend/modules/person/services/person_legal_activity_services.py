
from backend.apps.commerciall_api.main import db
from datetime import datetime, timezone
from backend.modules.utils.api_response import ApiResponse
from flask import current_app
from backend.modules.utils.api_response import json_response, ApiResponse
from ..models.person_legal_activity_model import PersonLegalActivity
import traceback
import uuid 

# upisert person legal activity function to create or update a record
def activity_upsert_service(data=None, person_uid_fk=None, apply_commit=True): 

    try:
        current_app.logger.debug("Received person legal activity data: %s", data)

        _data = PersonLegalActivity.from_json(data)
        
        if (_data.person_uid_fk is None or _data.person_uid_fk == "") or (_data.description is None or _data.description == ""):
            current_app.logger.debug("Missing required fields: person_uid_fk or description")
            if apply_commit:
                return json_response(
                    response=ApiResponse.MISSING_FIELDS,
                )
            else:
                return

        if _data.is_main:
            # Set all other person legal activities for this person to not main
            PersonLegalActivity.query.filter(PersonLegalActivity.person_uid_fk == _data.person_uid_fk, PersonLegalActivity.uid != _data.uid).update({"is_main": 0})

        _selected = db.session.get(PersonLegalActivity, _data.uid)
        
        if _selected:
            _selected.is_active = _data.is_active
            _selected.description = _data.description
            _selected.is_main = _data.is_main
            _selected.sync_status = _data.sync_status
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
            data={"person_legal_activity": persisted.to_dict()}
        )

    except Exception as e:
        raise
