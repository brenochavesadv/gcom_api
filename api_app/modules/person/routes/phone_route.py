from api_app.modules.person.models.mail_model import Mail
from main import db
from datetime import datetime
from flask import Blueprint, request
from ....constants.response import RESPONSE, json_response
from ..models.phone_model import Phone
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from sqlalchemy.exc import IntegrityError
import traceback

phone_bp = Blueprint("phone", __name__)

@phone_bp.route("/create", methods=["POST"])
@firebase_auth_required
def create_phone():
    try:
        phone_data = request.get_json()
        print("Received phone data:", phone_data)
        person_uid_fk = phone_data.get("person_uid_fk")
        phone = phone_data.get("phone")
        iso2alpha = phone_data.get("iso2alpha")
        type = phone_data.get("type")
        observation = phone_data.get("observation")
        is_active = phone_data.get("is_active", False)
        is_main = phone_data.get("is_main", False)

        if ((person_uid_fk is None or person_uid_fk == "") or (phone is None or phone == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        if Phone.query.filter_by(phone=phone, person_uid_fk=person_uid_fk).first():
            return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

        new_phone = Phone(
            person_uid_fk=person_uid_fk,
            phone=phone,
            iso2alpha=iso2alpha,
            type=type,
            observation=observation,
            is_active=1 if is_active else 0,
            is_main=1 if is_main else 0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.session.add(new_phone)
        db.session.commit()
    
        return json_response(uid=new_phone.uid, response="CREATED_SUCCESSFULLY", status_code=201)

    except Exception as e:
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)


@phone_bp.route("/update", methods=["PUT"])
@firebase_auth_required
def update_phone():
    try:
        phone_json = request.get_json()
        phone_data = phone_json.get("phone", {})
        uid = phone_data.get("uid")
        person_uid_fk = phone_data.get("person_uid_fk")
        phone = phone_data.get("phone")
        iso2alpha = phone_data.get("iso2alpha")
        type = phone_data.get("type")
        observation = phone_data.get("observation")
        is_active = phone_data.get("is_active")
        is_main = phone_data.get("is_main")
        print("Received phone update data:", phone_data)

        if ((uid is None or uid == "") or (phone is None or phone == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        phone_record = Phone.query.filter_by(uid=uid).first()
        if not phone_record:
            return json_response(uid=0, response="NOT_FOUND", status_code=404)
        
        if is_main:
            # Set all other phones for this person to not main
            Phone.query.filter(Phone.person_uid_fk == phone_record.person_uid_fk, Phone.uid != uid).update({"is_main": 0})
        else:
            # if there is no other main phone, set this one as main and active
            is_main_exists = Phone.query.filter_by(person_uid_fk=phone_record.person_uid_fk, is_main=1).first()
            if not is_main_exists:
                is_main = True
                is_active = True
        
        phone_record.person_uid_fk = person_uid_fk
        phone_record.phone = phone
        phone_record.iso2alpha = iso2alpha
        phone_record.type = type
        phone_record.observation = observation
        phone_record.is_active = 1 if is_active else 0
        phone_record.is_main = 1 if is_main else 0
        phone_record.updated_at = datetime.now()

        db.session.commit()

        return json_response(uid=phone_record.uid, response="UPDATED_SUCCESSFULLY", status_code=200)
    except IntegrityError as ie:
        db.session.rollback()
        # likely unique/foreign key constraint violation
        print("IntegrityError updating phone:", ie)
        print(traceback.format_exc())
        return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

    except Exception as e:
        db.session.rollback()
        # log full traceback for debugging
        print("Unexpected error updating phone:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@phone_bp.route("/list", methods=["GET"])
@firebase_auth_required
def list_phone_by_person():
    try:     
        # Get person_uid from query parameters
        uid = request.args.get("u")
        person_uid = request.args.get("p")

        if (uid is not None and uid != ""):
            phones = Phone.query.filter_by(uid=uid).first()
        elif (person_uid is not None and person_uid != ""):
            phones = Phone.query.filter_by(person_uid_fk=person_uid).all()
        else:
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        phone_list = [phone.to_dict() for phone in phones]

        return json_response(uid=0, response="OK", status_code=200, data=phone_list)

    except Exception as e:
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@phone_bp.route("/sync", methods=["GET"])
@firebase_auth_required
def list_phone_for_sync():
    try:     
        # Get person_uid from query parameters
        organization_uid = request.args.get("uid")
        last_update = request.args.get("date")

        if (organization_uid is None or organization_uid == "") or (last_update is None or last_update == ""):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        phones = Phone.query.filter_by(organization_uid_fk=organization_uid)
        phones = phones.filter(Phone.updated_at > last_update) 
        phones = phones.all()
        phone_list = [phone.to_dict() for phone in phones]

        return json_response(uid=0, response="OK", status_code=200, data=phone_list)

    except Exception as e:
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)