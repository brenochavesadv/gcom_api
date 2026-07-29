
from main import db
from datetime import datetime
from api_app.modules.utils.api_response import ApiResponse
from flask import current_app
from api_app.modules.utils.api_response import json_response, ApiResponse
from ..models.mail_model import Mail
import traceback

# upisert_mail function to create or update a mail record
def upinsert_mail(data=None, person_uid_fk=None, auto_commit=True): 

    try:
        current_app.logger.debug("Received mail data: %s", data)

        mail_data = Mail.from_json(data)

        if (mail_data.person_uid_fk in (None,"")) and person_uid_fk is not None:
            mail_data.person_uid_fk = person_uid_fk
        
        if (mail_data.person_uid_fk is None or mail_data.person_uid_fk == "") or (mail_data.email is None or mail_data.email == ""):
            current_app.logger.debug("Missing required fields: person_uid_fk or mail")

            if auto_commit:
                return json_response(
                    response=ApiResponse.MISSING_FIELDS,
                )
            else:
                return
                
        if mail_data.is_main:
            # Set all other mails for this person to not main
            Mail.query.filter(Mail.person_uid_fk == mail_data.person_uid_fk, Mail.uid != mail_data.uid).update({"is_main": 0})

        _selected = Mail.query.filter_by(uid=mail_data.uid).first() if mail_data.uid else None
        if not _selected:
            _selected = Mail.query.filter_by(person_uid_fk=mail_data.person_uid_fk, email=mail_data.email).first() if mail_data.person_uid_fk and mail_data.email else None

        if _selected:
            _selected.is_active = mail_data.is_active
            _selected.email = mail_data.email
            _selected.is_main = mail_data.is_main
            _selected.sync_status = mail_data.sync_status
            _selected.updated_at = datetime.now()
            response = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
        else:
            mail_data.created_at = datetime.now()
            mail_data.updated_at = datetime.now()
            db.session.add(mail_data)
            response = ApiResponse.CREATED_SUCCESSFULLY
            persisted = mail_data

        if auto_commit:
            db.session.commit()
        else:
            db.session.flush()

        return json_response(
            response=response,
            data={"mail": persisted.to_dict()}
        )

    except Exception as e:
        current_app.logger.debug("Error creating/updating mail: %s", e)
        current_app.logger.debug(traceback.format_exc())
        if auto_commit:
            db.session.rollback()
        else:
            db.session.flush()
            return 

    return json_response(response=ApiResponse.INTERNAL_ERROR)
    