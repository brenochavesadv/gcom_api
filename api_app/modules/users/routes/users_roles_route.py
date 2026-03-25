from main import db
from datetime import datetime
from flask import Blueprint, request
from ....constants.response import RESPONSE, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from sqlalchemy.exc import IntegrityError
import traceback
from ..models.users_roles_model import UsersRoles
from ..models.organization_model import Organization

users_roles_bp = Blueprint("roles", __name__)

@users_roles_bp.route("/create", methods=["POST"])
#@firebase_auth_required
def create_users_roles():
    try:
        data = request.get_json(silent=True) or {}
        role_payload = data.get("usersRoles") if isinstance(data.get("usersRoles"), dict) else data
        print("Received users roles data:", role_payload)
        users_roles = UsersRoles.get_data(role_payload)

        if ((users_roles['uid'] is None or users_roles['uid'] == "") or (users_roles['name'] is None or users_roles['name'] == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        if UsersRoles.query.filter_by(uid=users_roles['uid']).first() or UsersRoles.query.filter_by(name=users_roles['name']).first():
            return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

        db.session.add(UsersRoles(**users_roles))
        db.session.commit()
    
        return json_response(uid=users_roles['uid'], response="CREATED_SUCCESSFULLY", status_code=201)

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
        
        users_roles = UsersRoles.query.filter_by(uid=uid).first()
        if not users_roles:
            return json_response(uid=0, response="NOT_FOUND", status_code=404)

        duplicate_name = UsersRoles.query.filter(UsersRoles.name == name, UsersRoles.main_organization_uid_fk == org, UsersRoles.uid != uid).first()
        if duplicate_name:
            return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

        users_roles.name = name
        users_roles.main_organization_uid_fk = org
        users_roles.description = data.get("description")
        users_roles.allowed_app_routes = data.get("allowed_app_routes")
        users_roles.sync_status = data.get("sync_status","PENDING")
        users_roles.updated_at = datetime.now()

        db.session.commit()

        return json_response(uid=users_roles.uid, response="UPDATED_SUCCESSFULLY", status_code=200)

    except IntegrityError as ie:
        db.session.rollback()
        # likely unique/foreign key constraint violation
        print("IntegrityError updating users roles:", ie)
        print(traceback.format_exc())
        return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)
    
    except Exception as e:
        db.session.rollback()
        print("Error updating users roles:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@users_roles_bp.route("/list", methods=["GET"])
##@firebase_auth_required
def list_users_roles(): 

    try:     
        main_organization_uid = request.args.get("o")

        roles_query = UsersRoles.query

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