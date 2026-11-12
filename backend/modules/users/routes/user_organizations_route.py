from ast import If

from backend.apps.commerciall_api.main import db
from datetime import datetime
from flask import Blueprint, current_app, request
from ...utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from ..models.user_organizations_model import UserOrganizations
from ..models.user_profiles_model import UserProfiles
from ..models.user_keys_model import UserKeys
from firebase_admin import auth
from sqlalchemy.exc import IntegrityError

import uuid
import traceback

user_organizations_bp = Blueprint("u_orgs", __name__)

@user_organizations_bp.route("/list", methods=["POST"])
@firebase_auth_required
def list_users_organizations(): 

    try:
        data = request.get_json() or {}
        user_uid = data.get("uu") or None
        organization_uid = data.get("ou") or None

        if (user_uid in ("", None)):
                return json_response(response=ApiResponse.MISSING_FIELDS)

        query = UserOrganizations.query.filter_by(user_profiles_uid_fk=user_uid)

        if organization_uid not in ("", None):
            query = query.filter_by(organization_uid_fk=organization_uid)

        if query is None:
            return json_response(response=ApiResponse.NOT_FOUND)

        # Serialize data       
        result_data = []
        for item in query:
            result_data.append(item.to_dict())

        print(f"list_users_organizations result_data: {result_data}")
        
        return json_response(
            response = ApiResponse.OK,
            data = {"user_organizations": result_data}
        )

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
# upsert UserOrganizations and UserProfiles
@user_organizations_bp.route("/ui", methods=["POST"])
@firebase_auth_required
def upsert_user_orgranizations():
    try:
        data = request.get_json() or {}
        user_prof_payload = data.get("user_profiles", {})
        user_org_payload = data.get("user_organizations", {})
   
        user_prof = UserProfiles.from_json(user_prof_payload)
        user_org = UserOrganizations.from_json(user_org_payload)

        if ((user_org.organization_uid_fk in("",None)) or
            (user_org.person_uid_fk in("",None)) or
            (user_org.user_roles_uid_fk in("",None))):

                return json_response(response=ApiResponse.MISSING_FIELDS)
            
        # If user_profiles_uid is not provided, we need to create a new user_profiles, user_organizations, and user_keys 
        is_add = (user_org.user_profiles_uid_fk in ("", None))

        if is_add:
            if ((user_prof.mail in("",None)) or
                (user_prof.name in("",None))):

                    return json_response(response=ApiResponse.MISSING_FIELDS)

            # verify if the email exits in user_profiles
            existing_prof = UserProfiles.query.filter_by(mail=user_prof.mail).first()

            if existing_prof:
                # If the user already exists in User Profiles, we can use the existing UID
                user_prof.uid = existing_prof.uid
            else:
                # Resolve the Firebase UID first, then persist the local profile and keys.
                try:
                    firebase_user = auth.get_user_by_email(user_prof.mail)
                    firebase_uid = firebase_user.uid
                    current_app.logger.debug(f"Firebase user {firebase_user.email} found with UID: {firebase_uid}")

                except auth.UserNotFoundError:
                    if not user_prof.uid:
                        user_prof.uid = str(uuid.uuid4())

                    firebase_user = auth.create_user(
                        uid=user_prof.uid,
                        email=user_prof.mail,
                        display_name=user_org.user_name,
                    )

                    firebase_uid = firebase_user.uid
                    current_app.logger.debug(f"Firebase user created for {user_prof.mail} with UID: {firebase_uid}")

                user_prof.uid = firebase_uid
                user_prof.updated_at = datetime.now()
                user_prof.created_at = datetime.now()

                user_keys = UserKeys(
                    user_profiles_uid_fk=user_prof.uid,
                    pin_code=UserKeys.bcrypt_hash(str(uuid.uuid4()), user_prof.uid),
                    pw_offline=UserKeys.bcrypt_hash(str(uuid.uuid4()), user_prof.uid),
                    updated_at=datetime.now()
                )

                db.session.add(user_prof)
                db.session.add(user_keys)

            user_org.user_profiles_uid_fk = user_prof.uid

            # verify if the user_org exists in user_organizations
            existing_org = UserOrganizations.query.filter_by(person_uid_fk=user_org.person_uid_fk, organization_uid_fk=user_org.organization_uid_fk).first()

            if existing_org:
                existing_org.user_profiles_uid_fk = user_org.user_profiles_uid_fk
                existing_org.user_roles_uid_fk = user_org.user_roles_uid_fk
                existing_org.is_active = user_org.is_active
                existing_org.allowed_app_routes = user_org.allowed_app_routes
                existing_org.sync_status = "PENDING"
                existing_org.updated_at = datetime.now()

                db.session.commit()

                return json_response(
                    response=ApiResponse.UPDATED_SUCCESSFULLY,
                    data={"user_organizations": existing_org.to_dict()}
                )

            user_org.uid = str(uuid.uuid4())
            user_org.updated_at = datetime.now()
            user_org.created_at = datetime.now()

            db.session.add(user_org)
            
            db.session.commit()

            return json_response(
                response=ApiResponse.CREATED_SUCCESSFULLY,
                data={"user_organizations": user_org.to_dict()} # profiles and organizations are returned inside the user_organizations to_dict method
            )

        # update user_organizations   
        else:
            
            selected = UserOrganizations.query.filter_by(uid=user_org.uid).first()

            if selected is None:
                return json_response(response=ApiResponse.NOT_FOUND)  

            selected.user_roles_uid_fk = user_org.user_roles_uid_fk
            selected.is_active = user_org.is_active
            selected.allowed_app_routes = user_org.allowed_app_routes
            selected.sync_status = "PENDING"
            selected.updated_at = datetime.now()
                
            db.session.commit()

            return json_response(
                uid=user_org.uid,
                response=ApiResponse.CREATED_SUCCESSFULLY,
                data= {"user_organizations": user_org.to_dict()}
            )

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
