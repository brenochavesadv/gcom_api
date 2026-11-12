
from backend.apps.commerciall_api.main import db
from datetime import datetime, timezone
from backend.modules.utils.api_response import ApiResponse
from flask import current_app
from backend.modules.utils.api_response import json_response, ApiResponse
from ..models.phone_model import Phone
import traceback

# upisert phone function to create or update a phone record
def phone_upsert_service(data: None, person_uid_fk=None, apply_commit=True): 

    current_app.logger.debug("upsert_phone data: %s", data)

    try:
        _data = Phone.from_json(data)
        
        if (_data.person_uid_fk in (None,"")) and person_uid_fk is not None:
            _data.person_uid_fk = person_uid_fk

        if (_data.person_uid_fk is None or _data.person_uid_fk == "") or (_data.phone is None or _data.phone == ""):
            current_app.logger.debug("Missing required fields: person_uid_fk or phone")

            if apply_commit:
                return json_response(
                    response=ApiResponse.MISSING_FIELDS,
                )
            else:
                return

        if _data.is_main:
            # Set all other phones for this person to not main
            Phone.query.filter(Phone.person_uid_fk == _data.person_uid_fk, Phone.uid != _data.uid).update({"is_main": 0})
            
        _selected = db.session.get(Phone, _data.uid)

        if _selected:
            _selected.is_active = _data.is_active
            _selected.is_main = _data.is_main
            _selected.phone = _data.phone
            _selected.iso2alpha = _data.iso2alpha
            _selected.phone_type = _data.phone_type
            _selected.observation = _data.observation
            _selected.created_at = _selected.created_at
            _selected.updated_at = datetime.now(timezone.utc)
            _selected.sync_status = "PENDING"
            
            response = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
            
        else:
            #from uuid import uuid4 as Uuid4
            #_data.uid = Uuid4() // db uses integer auto increment for primary key, so no need to set uid manually
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
            data={"phone": persisted.to_dict()}
        )

    except Exception as e:
        raise


def phone_list_service(data):
    try:     
        # Get person_uid from query parameters
        data = data.get_json()
        uid = data.get("u")
        person_uid = data.get("p")
        current_app.logger.debug("Received phone data:", data)
        
        if (uid is not None and uid != ""):
            phones = Phone.query.get(uid=uid)
        elif (person_uid is not None and person_uid != ""):
            phones = Phone.query.first(person_uid_fk=person_uid)
        else:
            return json_response(response=ApiResponse.MISSING_FIELDS)
        
        phone_list = [phone .to_dict() for phone in phones]

        return json_response(response=ApiResponse.OK, data=phone_list)

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise


def phone_sync_service(data=None):
    try:     
        # Get person_uid from query parameters
        organization_uid = data.get("uid")
        last_update = data.get("date")

        if (organization_uid is None or organization_uid == "") or (last_update is None or last_update == ""):
            return json_response(response=ApiResponse.MISSING_FIELDS)

        phones = Phone.query.filter_by(organization_uid_fk=organization_uid)
        phones = phones.filter(Phone.updated_at > last_update) 
        phones = phones.all()
        phone_list = [phone.to_dict() for phone in phones]

        return json_response(response=ApiResponse.OK, data=phone_list)

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise

