from main import db
from datetime import datetime
from flask import Blueprint, request
from ....constants.response import RESPONSE, json_response
from ..models.address_suffix_model import AddressSuffix
from ..models.address_unit_model import AddressUnit
from ..models.address_model import Address
from ...auth_firebase.firebase_decorators import firebase_auth_required
from sqlalchemy.exc import IntegrityError
import traceback

address_bp = Blueprint("address", __name__)

@address_bp.route("/suffix", methods=["GET"])
@firebase_auth_required
def list_suffix():
    try:
        suffixes = AddressSuffix.query.all()
        suffix_list = [suffix.to_dict() for suffix in suffixes]

        return json_response(uid=0, response="OK", status_code=200, data=suffix_list)

    except Exception as e:
        ## show the traceback error in the console
        import traceback
        print("[ERROR] /address/suffix exception:", e)
        traceback.print_exc() 
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)

@address_bp.route("/unit", methods=["GET"])
@firebase_auth_required
def list_units():
    try:
        units = AddressUnit.query.all()
        unit_list = [unit.to_dict() for unit in units]

        return json_response(response="OK", status_code=200, data=unit_list)

    except Exception as e:
        ## show the traceback error in the console
        ##import traceback
        ##print("[ERROR] /address/unit exception:", e)
        ##traceback.print_exc() 
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@address_bp.route("/list", methods=["GET"])
@firebase_auth_required
def list_address():
    try:

        uid = request.args.get("u")
        person_uid = request.args.get("p")
        address = []

        if (uid is not None and uid != ""):
            address = Address.query.filter_by(uid=uid).all()
        elif (person_uid is not None and person_uid != ""):
            address = Address.query.filter_by(person_uid_fk=person_uid).all()
        else:
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        address_list = [addr.to_dict() for addr in address]

        return json_response(uid=0, response="OK", status_code=200, data=address_list)

    except Exception as e:
        ## show the traceback error in the console
        #import traceback
        #print("[ERROR] /address/unit exception:", e)
        #traceback.print_exc() 
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)


@address_bp.route("/create", methods=["POST"])
@firebase_auth_required
def create_address():
    try:
        address_data = request.get_json()
        print("Received address data:", address_data)
        person_uid_fk = address_data.get("person_uid_fk")
        address = address_data.get("address")
        organization = address_data.get("organization_uid_fk")

        if ((person_uid_fk is None or person_uid_fk == "") or (address is None or address == "") or (organization is None or organization == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        if Address.query.filter_by(address=address, person_uid_fk=person_uid_fk).first():
            return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

        # Create objects using factory
        address = Address.address_data(address_data, is_create=True)
        db.session.add(address)
        db.session.commit()
    
        return json_response(uid=address.uid, response="CREATED_SUCCESSFULLY", status_code=201)

    except Exception as e:
        db.session.rollback()
        print("[ERROR] /address/create exception:", e)
        traceback.print_exc()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)


@address_bp.route("/update", methods=["PUT"])
@firebase_auth_required
def update_address():
    try:
        address_json = request.get_json()
        address_data = address_json.get("address", {})
        uid = address_data.get("uid")
        address = address_data.get("address")
        is_active = address_data.get("is_active")
        is_main = address_data.get("is_main")
        print("Received address update data:", address_data)

        if ((uid is None or uid == "") or (address is None or address == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        address_record = Address.query.filter_by(uid=uid).first()
        if not address_record:
            return json_response(uid=0, response="NOT_FOUND", status_code=404)
        
        if is_main:
            # Set all other addresses for this person to not main
            Address.query.filter(Address.person_uid_fk == address_record.person_uid_fk, Address.uid != uid).update({"is_main": 0})
        else:
            # if there is no other main address, set this one as main and active
            is_main_exists = Address.query.filter_by(person_uid_fk=address_record.person_uid_fk, is_main=1).first()
            if not is_main_exists:
                is_main = True
                is_active = True
        
        address_record.address = address
        address_record.address_label = address_data.get("address_label")
        address_record.suffix = address_data.get("suffix")
        address_record.number = address_data.get("number")
        address_record.complement = address_data.get("complement")
        address_record.nbhd = address_data.get("nbhd")
        address_record.zip_code = address_data.get("zip_code")
        address_record.city_code = address_data.get("city_code")
        address_record.city_name = address_data.get("city_name")
        address_record.state_abbrev = address_data.get("state_abbrev")
        address_record.state_name = address_data.get("state_name")
        address_record.country_iso2alpha = address_data.get("country_iso2alpha")
        address_record.is_active = 1 if is_active else 0
        address_record.is_main = 1 if is_main else 0

        db.session.commit()

        return json_response(uid=address_record.uid, response="UPDATED_SUCCESSFULLY", status_code=200)
    except IntegrityError as ie:
        db.session.rollback()
        # likely unique/foreign key constraint violation
        print("IntegrityError updating address:", ie)
        print(traceback.format_exc())
        return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

    except Exception as e:
        db.session.rollback()
        # log full traceback for debugging
        print("Unexpected error updating address:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    