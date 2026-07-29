from flask import Blueprint, current_app, request, current_app
from ...utils.api_response import ApiResponse, json_response
from ..models.address_suffix_model import AddressSuffix
from ..models.address_unit_model import AddressUnit
from ..models.address_model import Address
from ..services.address_services import upinsert_address
from ...auth_firebase.firebase_decorators import firebase_auth_required

address_bp = Blueprint("address", __name__)

@address_bp.route("/suffix", methods=["GET"])
@firebase_auth_required
def list_suffix():
    try:
        suffixes = AddressSuffix.query.all()
        suffix_list = [suffix.to_dict() for suffix in suffixes]

        return json_response(response=ApiResponse.REQUEST_SUCCESSFUL, data=suffix_list)

    except Exception as e:
        ## show the traceback error in the console
        import traceback
        current_app.logger.debug("[ERROR] /address/suffix exception: %s", e)
        traceback.print_exc()
        return json_response(response="INTERNAL_ERROR")

@address_bp.route("/unit", methods=["GET"])
@firebase_auth_required
def list_units():
    try:
        units = AddressUnit.query.all()
        unit_list = [unit.to_dict() for unit in units]

        return json_response(response=ApiResponse.REQUEST_SUCCESSFUL, data=unit_list)

    except Exception as e:
        ## show the traceback error in the console
        ##import traceback
        ##current_app.logger.debug("[ERROR] /address/unit exception:", e)
        ##traceback.print_exc() 
        return json_response(response=ApiResponse.INTERNAL_ERROR)

@address_bp.route("/list", methods=["POST"])
@firebase_auth_required
def list_address():
    try:
        data = request.get_json()
        uid = data.get("u")
        person_uid = data.get("p")
        address = []

        if (uid is not None and uid != ""):
            address = Address.query.filter_by(uid=uid).all()
        elif (person_uid is not None and person_uid != ""):
            address = Address.query.filter_by(person_uid_fk=person_uid).all()
        else:
            return json_response(response=ApiResponse.MISSING_FIELDS)

        address_list = [addr.to_dict() for addr in address]

        return json_response(response=ApiResponse.REQUEST_SUCCESSFUL, data=address_list)

    except Exception as e:
        ## show the traceback error in the console
        #import traceback
        #current_app.logger.debug("[ERROR] /address/unit exception:", e)
        #traceback.print_exc() 
        return json_response(response=ApiResponse.INTERNAL_ERROR)


## upinsert route to create or update an address record
@address_bp.route("/ui", methods=["POST"])
@firebase_auth_required
def ui_address():
        data = request.get_json()
        return upinsert_address(data=data)