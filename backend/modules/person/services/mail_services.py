

from backend.apps.commerciall_api.main import db
from datetime import datetime, timezone
from backend.modules.utils.api_response import ApiResponse
from flask import current_app
from backend.modules.utils.api_response import json_response, ApiResponse
from backend.modules.utils.get_date_on_utc import getDateOnUTC
from ..models.mail_model import Mail
import traceback

# upisertdata function to create or update a mail record
def mail_upsert_service(data: None, person_uid_fk=None, apply_commit=True): 

    try:
        _data = Mail.from_json(data)
        
        current_app.logger.debug("Received mail data: %s", data)

        if (_data.person_uid_fk in (None,"")) and person_uid_fk is not None:
            _data.person_uid_fk = person_uid_fk
        
        if (_data.person_uid_fk is None or _data.person_uid_fk == "") or (_data.email is None or _data.email == ""):
            current_app.logger.debug("Missing required fields: person_uid_fk or mail")

            if apply_commit:
                return json_response(
                    response=ApiResponse.MISSING_FIELDS,
                )
            else:
                return
                
        if _data.is_main:
            # Set all other mails for this person to not main
            Mail.query.filter(Mail.person_uid_fk == _data.person_uid_fk, Mail.uid != _data.uid).update({"is_main": 0})

        _selected = db.session.get(Mail, _data.uid)

        if _selected:
            _selected.is_active = _data.is_active
            _selected.email = _data.email
            _selected.is_main = _data.is_main
            _selected.sync_status = _data.sync_status
            _selected.created_at = getDateOnUTC(_selected.created_at)
            _selected.updated_at = getDateOnUTC(None)
            _selected.sync_status = "PENDING"
            response = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
        else:
            #from uuid import uuid4 as Uuid4
            #_data.uid = Uuid4() // db uses integer auto increment for primary key, so no need to set uid manually
            _data.created_at = getDateOnUTC(None)
            _data.updated_at = getDateOnUTC(None)
            _data.sync_status = "PENDING"
            db.session.add(_data)
            response = ApiResponse.CREATED_SUCCESSFULLY
            persisted = _data

        print(f"Persisted mail: {persisted.to_dict()}")

        if apply_commit:
            db.session.commit()

        return json_response(
            response=response,
            data={"mail": persisted.to_dict()}
        )

    except Exception as e:
        raise
    
