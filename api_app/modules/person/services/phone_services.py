
from main import db
from datetime import datetime
from api_app.modules.utils.api_response import ApiResponse
from flask import current_app
from api_app.modules.utils.api_response import json_response, ApiResponse
from ..models.phone_model import Phone
import traceback

# upisert phone function to create or update a phone record
def upinsert_phone(data=None, person_uid_fk=None, auto_commit=True): 

    current_app.logger.debug("upinsert_phone data: %s", data)

    try:

        phone_data = Phone.from_json(data)
        
        if (phone_data.person_uid_fk in (None,"")) and person_uid_fk is not None:
            phone_data.person_uid_fk = person_uid_fk

        if (phone_data.person_uid_fk is None or phone_data.person_uid_fk == "") or (phone_data.phone is None or phone_data.phone == ""):
            current_app.logger.debug("Missing required fields: person_uid_fk or phone")

            if auto_commit:
                return json_response(
                    response=ApiResponse.MISSING_FIELDS,
                )
            else:
                return

        if phone_data.is_main:
            # Set all other phones for this person to not main
            Phone.query.filter(Phone.person_uid_fk == phone_data.person_uid_fk, Phone.uid != phone_data.uid).update({"is_main": 0})
            
        _selected = Phone.query.filter_by(uid=phone_data.uid).first() if phone_data.uid else None
        if not _selected:
            _selected = Phone.query.filter_by(person_uid_fk=phone_data.person_uid_fk, phone=phone_data.phone).first() if phone_data.person_uid_fk and phone_data.phone else None

        if _selected:
            _selected.is_active = phone_data.is_active
            _selected.is_main = phone_data.is_main
            _selected.phone = phone_data.phone
            _selected.iso2alpha = phone_data.iso2alpha
            _selected.phone_type = phone_data.phone_type
            _selected.observation = phone_data.observation
            _selected.updated_at = datetime.now()
            
            response = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
            
        else:
            phone_data.created_at = datetime.now()
            phone_data.updated_at = datetime.now()
            db.session.add(phone_data)
            response = ApiResponse.CREATED_SUCCESSFULLY
            persisted = phone_data

        if auto_commit:
            db.session.commit()
        else:
            db.session.flush()

        return json_response(
            response=response,
            data={"phone": persisted.to_dict()}
        )

    except Exception as e:
        current_app.logger.debug("Error creating/updating phone: %s", e)
        current_app.logger.debug(traceback.format_exc())
        if auto_commit:
            db.session.rollback()
        else:
            db.session.flush()
            return

    return json_response(response=ApiResponse.INTERNAL_ERROR, exception=str(e))
    