from main import db
from datetime import datetime
from flask import Blueprint, current_app, request
from ...utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
import traceback
from ..models.user_roles_model import UserRoles
import uuid

users_roles_bp = Blueprint("roles", __name__)

@users_roles_bp.route("/ui", methods=["POST"])
@firebase_auth_required
def users_roles_upinsert():
    try:
        data = request.get_json() or {}
        role_payload = data.get("user_roles")
        
        current_app.logger.debug("Received users roles data: %s", role_payload)
        user_roles = UserRoles.from_json(role_payload)
        existing_role = None

        if (user_roles.name in ("", None)) or (user_roles.main_organization_uid_fk in ("", None)):
            return json_response(response=ApiResponse.MISSING_FIELDS)       

        query = UserRoles.query

        if user_roles.uid:
            existing_role = query.filter_by(uid=user_roles.uid).first()
            
            if existing_role:
                # Update existing role
                existing_role.name = user_roles.name
                existing_role.description = user_roles.description
                existing_role.sync_status = user_roles.sync_status
                existing_role.updated_at = datetime.now()
                persisted_role = existing_role

            else:
                return json_response(response=ApiResponse.NOT_FOUND)
                
        else:
            # Create new role
            query = query.filter(
                UserRoles.name == user_roles.name,
                UserRoles.main_organization_uid_fk == user_roles.main_organization_uid_fk,
            )
            if query.count() > 0:
                return json_response(response=ApiResponse.DUPLICATE_ENTRY) 

            user_roles.uid = str(uuid.uuid4())
            user_roles.created_at = datetime.now()
            user_roles.updated_at = datetime.now()
            persisted_role = user_roles
            db.session.add(user_roles)
            
        db.session.commit()

        if existing_role:
            response = ApiResponse.UPDATED_SUCCESSFULLY
        else:
            response = ApiResponse.CREATED_SUCCESSFULLY
            
        return json_response(response=response, data={"user_roles": persisted_role.to_dict()})

    except Exception as e:
        db.session.rollback()
        return json_response(response=ApiResponse.INTERNAL_ERROR)


@users_roles_bp.route("/uar", methods=["POST"])
@firebase_auth_required
def user_roles_update_allowed_routes():
    try:
        data = request.get_json() or {}
        uid = data.get("uid")
        routes = data.get("routes").replace("[", "").replace("]", "").replace(" ", "")

        if uid in (None, "") or routes in (None, ""):
            return json_response(response=ApiResponse.MISSING_FIELDS)

        selected_role = UserRoles.query.filter_by(uid=uid).first()

        if not selected_role:
            return json_response(response=ApiResponse.NOT_FOUND)

        selected_role.allowed_app_routes = routes
        selected_role.updated_at = datetime.now()
            
        db.session.commit()
            
        return json_response(response=ApiResponse.UPDATED_SUCCESSFULLY, data={"user_roles": selected_role.to_dict()})

    except Exception as e:
        db.session.rollback()
        return json_response(response=ApiResponse.INTERNAL_ERROR)

@users_roles_bp.route("/list", methods=["POST"])
#@firebase_auth_required
def list_users_roles(): 

    try:     
        main_organization_uid = request.get_json().get("o")

        roles_query = UserRoles.query

        if (main_organization_uid is not None and main_organization_uid != ""):
            roles_query = roles_query.filter_by(main_organization_uid_fk=main_organization_uid)
        else:
            return json_response(response=ApiResponse.MISSING_FIELDS)

        # Serialize data       
        data = []
        for role in roles_query:
            data.append(role.to_dict())
        
        return json_response(
            response = ApiResponse.OK,
            data = data
        )

    except Exception as e:
        current_app.logger.debug("Error listing users roles:", e)
        current_app.logger.debug(traceback.format_exc())
        return json_response(response=ApiResponse.INTERNAL_ERROR)

@users_roles_bp.route("/sync", methods=["GET"])
@firebase_auth_required
def list_users_roles_for_sync():
    try:     
        # Get person_uid from query parameters
        users_roles_uid = request.args.get("uid")
        last_update = request.args.get("date")

        if (users_roles_uid is None or users_roles_uid == "") or (last_update is None or last_update == ""):
            return json_response(response=ApiResponse.MISSING_FIELDS)

        roles = UserRoles.query.filter_by(uid=users_roles_uid)
        roles = roles.filter(UserRoles.updated_at > last_update) 
        roles = roles.all()
        roles_list = [role.to_dict() for role in roles]

        return json_response(response=ApiResponse.OK, data=roles_list)

    except Exception as e:
        return json_response(response=ApiResponse.INTERNAL_ERROR)