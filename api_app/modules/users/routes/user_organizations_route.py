from main import db
from datetime import datetime
from flask import Blueprint, request
from ....constants.response import RESPONSE, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
import traceback
from ..models.user_organizations_model import UserOrganizations

user_organizations_bp = Blueprint("u_orgs", __name__)

@user_organizations_bp.route("/list", methods=["POST"])
#@firebase_auth_required
def list_users_organizations(): 

    try:     
        user_uid = request.get_json().get("u") or None

        user_orgs_query = UserOrganizations.query

        if (user_uid is not None and user_uid != ""):
            print("Fetching users organizations by user uid:", user_uid)
            user_orgs_query = user_orgs_query.filter_by(user_profiles_uid_fk=user_uid)
        else:
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        # Serialize data       
        data = []
        for user in user_orgs_query:
            data.append(user.to_dict())
        
        return json_response(
            response = "OK",
            status_code = 200,
            data = data
        )

    except Exception as e:
        print("Error listing users organizations:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
