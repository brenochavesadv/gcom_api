from main import db
from datetime import datetime
from flask import Blueprint, request
from ....constants.response import RESPONSE, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
import traceback
from ..models.user_roles_model import UserRoles
from ..models.organization_model import Organization

users_roles_bp = Blueprint("roles", __name__)

@users_roles_bp.route("/create", methods=["POST"])
#@firebase_auth_required
def create_users_roles():
    try:
        data = request.get_json(silent=True) or {}
        role_payload = data.get("usersRoles") if isinstance(data.get("usersRoles"), dict) else data
        print("Received users roles data:", role_payload)
        user_roles = UserRoles.get_data(role_payload)

        if ((user_roles['uid'] is None or user_roles['uid'] == "") or (user_roles['name'] is None or user_roles['name'] == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        if UserRoles.query.filter_by(uid=user_roles['uid']).first() or UserRoles.query.filter_by(name=user_roles['name']).first():
            return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

        db.session.add(UserRoles(**user_roles))
        db.session.commit()
    
        return json_response(uid=user_roles['uid'], response="CREATED_SUCCESSFULLY", status_code=201)

    except Exception as e:
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)


@users_roles_bp.route("/update", methods=["PUT"])
#@firebase_auth_required
def update_users_roles():
    try:

        json = request.get_json() or {}
        data = json.get("usersRoles") if isinstance(json.get("usersRoles"), dict) else json
        print("Received users roles update data:", data)
        uid = data.get("uid")
        name = data.get("name")
        org = data.get("main_organization_uid_fk")

        if ((uid is None or uid == "") or (name is None or name == "") or (org is None or org == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        user_roles = UserRoles.query.filter_by(uid=uid).first()
        if not user_roles:
            return json_response(uid=0, response="NOT_FOUND", status_code=404)

        duplicate_name = UserRoles.query.filter(UserRoles.name == name, UserRoles.main_organization_uid_fk == org, UserRoles.uid != uid).first()
        if duplicate_name:
            return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

        user_roles.name = name
        user_roles.main_organization_uid_fk = org
        user_roles.description = data.get("description")
        user_roles.allowed_app_routes = data.get("allowed_app_routes")
        user_roles.sync_status = data.get("sync_status","PENDING")
        user_roles.updated_at = datetime.now()

        db.session.commit()

        return json_response(uid=user_roles.uid, response="UPDATED_SUCCESSFULLY", status_code=200)
    
    except Exception as e:
        db.session.rollback()
        print("Error updating users roles:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@users_roles_bp.route("/list", methods=["POST"])
##@firebase_auth_required
def list_users_roles(): 

    try:     
        main_organization_uid = request.get_json().get("o")

        roles_query = UserRoles.query

        if (main_organization_uid is not None and main_organization_uid != ""):
            print("Fetching users roles by organization main uid:", main_organization_uid)
            roles_query = roles_query.filter_by(main_organization_uid_fk=main_organization_uid)
        else:
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        # Serialize data       
        data = []
        for role in roles_query:
            data.append(role.to_dict())
        
        return json_response(
            response = "OK",
            status_code = 200,
            data = data
        )

    except Exception as e:
        print("Error listing users roles:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@users_roles_bp.route("/sync", methods=["GET"])
#@firebase_auth_required
def list_users_roles_for_sync():
    try:     
        # Get person_uid from query parameters
        users_roles_uid = request.args.get("uid")
        last_update = request.args.get("date")

        if (users_roles_uid is None or users_roles_uid == "") or (last_update is None or last_update == ""):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        org = Organization.query.filter_by(users_roles_uid_fk=users_roles_uid)
        org = org.filter(Organization.updated_at > last_update) 
        org = org.all()
        org_list = [org.to_dict() for org in org]

        return json_response(uid=0, response="OK", status_code=200, data=org_list)

    except Exception as e:
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)