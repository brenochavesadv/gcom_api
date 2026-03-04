from main import db
from datetime import datetime
from flask import Blueprint, request
from ....constants.response import RESPONSE, json_response
from ..models.mail_model import Mail
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from sqlalchemy.exc import IntegrityError
import traceback

mail_bp = Blueprint("mail", __name__)

@mail_bp.route("/create", methods=["POST"])
@firebase_auth_required
def create_mail():
    try:
        mail_data = request.get_json()
        print("Received mail data:", mail_data)
        person_uid_fk = mail_data.get("person_uid_fk")
        email = mail_data.get("email")
        is_active = mail_data.get("is_active", False)
        is_main = mail_data.get("is_main", False)

        if ((person_uid_fk is None or person_uid_fk == "") or (email is None or email == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        
        if Mail.query.filter_by(email=email, person_uid_fk=person_uid_fk).first():
            return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

        new_mail = Mail(
            person_uid_fk=person_uid_fk,
            email=email,
            is_active=1 if is_active else 0,
            is_main=1 if is_main else 0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.session.add(new_mail)
        db.session.commit()
    
        return json_response(uid=new_mail.uid, response="CREATED_SUCCESSFULLY", status_code=201)

    except Exception as e:
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)


@mail_bp.route("/update", methods=["PUT"])
@firebase_auth_required
def update_mail():
    try:
        mail_data = request.get_json()
        mail = mail_data.get("mail", {})
        uid = mail.get("uid")
        is_active = mail.get("is_active")
        is_main = mail.get("is_main")
        email = mail.get("email")
        print("Received mail update data:", mail)

        if ((uid is None or uid == "") or (email is None or email == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        mail_record = Mail.query.filter_by(uid=uid).first()
        if not mail_record:
            return json_response(uid=0, response="NOT_FOUND", status_code=404)
        
        if is_main:
            # Set all other mails for this person to not main
            Mail.query.filter(Mail.person_uid_fk == mail_record.person_uid_fk, Mail.uid != uid).update({"is_main": 0})
        else:
            # if there is no other main email, set this one as main and active
            is_main_exists = Mail.query.filter_by(person_uid_fk=mail_record.person_uid_fk, is_main=1).first()
            if not is_main_exists:
                is_main = True
                is_active = True
        
        mail_record.email = email
        mail_record.is_active = 1 if is_active else 0
        mail_record.is_main = 1 if is_main else 0
        mail_record.updated_at = datetime.now()

        db.session.commit()

        return json_response(uid=mail_record.uid, response="UPDATED_SUCCESSFULLY", status_code=200)

    except IntegrityError as ie:
        db.session.rollback()
        # likely unique/foreign key constraint violation
        print("IntegrityError updating mail:", ie)
        print(traceback.format_exc())
        return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

    except Exception as e:
        db.session.rollback()
        # log full traceback for debugging
        print("Unexpected error updating mail:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)

@mail_bp.route("/list", methods=["GET"])
@firebase_auth_required
def list_mail():
    try:     
        # Get person_uid from query parameters
        uid = request.args.get("u") 
        person_uid = request.args.get("p")


        if (uid is not None and uid != ""):
            print("Fetching mail by uid:", uid)
            mails = Mail.query.filter_by(uid=uid).first()
        elif (person_uid is not None and person_uid != ""):
            print("Fetching mails by person_uid:", person_uid)
            mails = Mail.query.filter_by(person_uid_fk=person_uid).all()
        else:
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        mail_list = [mail.to_dict() for mail in mails]

        return json_response(uid=0, response="OK", status_code=200, data=mail_list)

    except Exception as e:
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@mail_bp.route("/sync", methods=["GET"])
@firebase_auth_required
def list_mail_for_sync():
    try:     
        # Get person_uid from query parameters
        organization_uid = request.args.get("uid")
        last_update = request.args.get("date")

        if (organization_uid is None or organization_uid == "") or (last_update is None or last_update == ""):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        mails = Mail.query.filter_by(organization_uid_fk=organization_uid)
        mails = mails.filter(Mail.updated_at > last_update) 
        mails = mails.all()
        mail_list = [mail.to_dict() for mail in mails]

        return json_response(uid=0, response="OK", status_code=200, data=mail_list)

    except Exception as e:
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)