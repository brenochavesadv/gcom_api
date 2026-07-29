from main import db
from flask import Blueprint, current_app, request
from ...utils.api_response import ApiResponse, json_response
from ..models.phone_model import Phone
from ...auth_firebase.firebase_decorators import firebase_auth_required
from ..services.phone_services import upinsert_phone

phone_bp = Blueprint("phone", __name__)

@phone_bp.route("/ui", methods=["POST"])
@firebase_auth_required
def ui_phone():
        data = request.get_json()
        return upinsert_phone(data=data)

@phone_bp.route("/list", methods=["POST"])
@firebase_auth_required
def list_phone_by_person():
    try:     
        # Get person_uid from query parameters
        data = request.get_json()
        uid = data.get("u")
        person_uid = data.get("p")
        current_app.logger.debug("Received phone data:", data)
        if (uid is not None and uid != ""):
            phones = Phone.query.filter_by(uid=uid).first()
        elif (person_uid is not None and person_uid != ""):
            phones = Phone.query.filter_by(person_uid_fk=person_uid).all()
        else:
            return json_response(response=ApiResponse.MISSING_FIELDS)
        
        phone_list = [phone.to_dict() for phone in phones]

        return json_response(response=ApiResponse.OK, data=phone_list)

    except Exception as e:
        return json_response(response=ApiResponse.INTERNAL_ERROR, exception=str(e))

@phone_bp.route("/sync", methods=["GET"])
@firebase_auth_required
def list_phone_for_sync():
    try:     
        # Get person_uid from query parameters
        organization_uid = request.args.get("uid")
        last_update = request.args.get("date")

        if (organization_uid is None or organization_uid == "") or (last_update is None or last_update == ""):
            return json_response(response=ApiResponse.MISSING_FIELDS)

        phones = Phone.query.filter_by(organization_uid_fk=organization_uid)
        phones = phones.filter(Phone.updated_at > last_update) 
        phones = phones.all()
        phone_list = [phone.to_dict() for phone in phones]

        return json_response(response=ApiResponse.OK, data=phone_list)

    except Exception as e:
        return json_response(response=ApiResponse.INTERNAL_ERROR, exception=str(e))