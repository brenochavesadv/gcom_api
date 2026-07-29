
from main import db
from datetime import datetime
from api_app.modules.utils.api_response import ApiResponse
from flask import current_app
from api_app.modules.utils.api_response import json_response, ApiResponse
from ..models.person_legal_activity_model import PersonLegalActivity
import traceback
import uuid 

# upisert person legal activity function to create or update a record
def upinsert_pl_activity(data=None, person_uid_fk=None, auto_commit=True): 

    try:
        current_app.logger.debug("Received person legal activity data: %s", data)

        activity_data = PersonLegalActivity.from_json(data)

        if (activity_data.person_uid_fk in (None,"")) and person_uid_fk is not None:
            activity_data.person_uid_fk = person_uid_fk
        
        if (activity_data.person_uid_fk is None or activity_data.person_uid_fk == "") or (activity_data.description is None or activity_data.description == ""):
            current_app.logger.debug("Missing required fields: person_uid_fk or description")
            if auto_commit:
                return json_response(
                    response=ApiResponse.MISSING_FIELDS,
                )
            else:
                return

        if activity_data.is_main:
            # Set all other person legal activities for this person to not main
            PersonLegalActivity.query.filter(PersonLegalActivity.person_uid_fk == activity_data.person_uid_fk, PersonLegalActivity.uid != activity_data.uid).update({"is_main": 0})

        _selected = PersonLegalActivity.query.filter_by(uid=activity_data.uid).first() if activity_data.uid else None
        if not _selected:
            _selected = PersonLegalActivity.query.filter_by(person_uid_fk=activity_data.person_uid_fk, activity_code=activity_data.activity_code).first() if activity_data.person_uid_fk and activity_data.activity_code else None

        if _selected:
            _selected.is_active = activity_data.is_active
            _selected.description = activity_data.description
            _selected.is_main = activity_data.is_main
            _selected.sync_status = activity_data.sync_status
            _selected.updated_at = datetime.now()
            response = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
        else:
            activity_data.uid = str(uuid.uuid4())
            activity_data.created_at = datetime.now()
            activity_data.updated_at = datetime.now()
            db.session.add(activity_data)
            response = ApiResponse.CREATED_SUCCESSFULLY
            persisted = activity_data

        if auto_commit:
            db.session.commit()
        else:
            db.session.flush()

        return json_response(
            response=response,
            data={"person_legal_activity": persisted.to_dict()}
        )

    except Exception as e:
        current_app.logger.debug("Error creating/updating person legal activity: %s", e)
        current_app.logger.debug(traceback.format_exc())
        if auto_commit:
            db.session.rollback()
        else:
            db.session.flush()
            return

    return json_response(response=ApiResponse.INTERNAL_ERROR)
