from flask import Blueprint, current_app, request
from ...utils.api_response import ApiResponse, json_response
from ..models.mail_model import Mail
from ...auth_firebase.firebase_decorators import firebase_auth_required
from ..services.mail_services import upsert_mail

mail_bp = Blueprint("pmail", __name__)

@mail_bp.route("/uim", methods=["POST"])
@firebase_auth_required
def ui_mail():
    data = request.get_json()
    return upsert_mail(data=data)
       

@mail_bp.route("/list", methods=["POST"])
@firebase_auth_required
def list_mail():
    try:     
        # Get person_uid from query parameters
        data = request.get_json()
        uid = data.get("u")
        person_uid = data.get("p")

        if (uid is not None and uid != ""):
            current_app.logger.debug("Fetching mail by uid:", uid)
            mails = Mail.query.filter_by(uid=uid).first()
        elif (person_uid is not None and person_uid != ""):
            current_app.logger.debug("Fetching mails by person_uid:", person_uid)
            mails = Mail.query.filter_by(person_uid_fk=person_uid).all()
        else:
            return json_response(response=ApiResponse.MISSING_FIELDS)

        mail_list = [mail.to_dict() for mail in mails]

        return json_response(response=ApiResponse.REQUEST_SUCCESSFUL, data=mail_list)

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
@mail_bp.route("/sync", methods=["GET"])
@firebase_auth_required
def list_mail_for_sync():
    try:     
        # Get person_uid from query parameters
        organization_uid = request.args.get("uid")
        last_update = request.args.get("date")

        if (organization_uid is None or organization_uid == "") or (last_update is None or last_update == ""):
            return json_response(response=ApiResponse.MISSING_FIELDS)

        mails = Mail.query.filter_by(organization_uid_fk=organization_uid)
        mails = mails.filter(Mail.updated_at > last_update) 
        mails = mails.all()
        mail_list = [mail.to_dict() for mail in mails]

        return json_response(response=ApiResponse.REQUEST_SUCCESSFUL, data=mail_list)

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
