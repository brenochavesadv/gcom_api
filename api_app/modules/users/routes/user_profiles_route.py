import random
import traceback

from main import db
from datetime import datetime
from flask import Blueprint, current_app, request
from ...utils.api_response import ApiResponse, json_response
from ..models.user_profiles_model import UserProfiles   
from ..models.user_organizations_model import UserOrganizations
from ..models.user_keys_model import UserKeys
from ...auth_firebase.firebase_decorators import firebase_auth_required
from sqlalchemy.exc import IntegrityError
from ...mail.smtp_services import send_email_smtp, smtp_info

user_profiles_bp = Blueprint("profiles", __name__)

    
@user_profiles_bp.route("/u", methods=["PUT"])
@firebase_auth_required
def update_profile():
    try:
        data = request.get_json() or {}         
        profile_data = UserProfiles.from_json(data.get("user_profiles", {}))

        if ((profile_data.uid is None or profile_data.uid == "") 
            or (profile_data.display_name is None or profile_data.display_name == "")):   
            return json_response(response=ApiResponse.MISSING_FIELDS)

        new_profile = UserProfiles.query.filter_by(uid=profile_data.uid).first()
        if not new_profile:
            return json_response(response=ApiResponse.NOT_FOUND)

        new_profile.display_name = profile_data.display_name
        new_profile.location = profile_data.location
        new_profile.language_code = profile_data.language_code
        new_profile.iso2_alpha = profile_data.iso2_alpha
        new_profile.date_format = profile_data.date_format
        new_profile.default_organization_uid_fk = profile_data.default_organization_uid_fk
        new_profile.updated_at = profile_data.updated_at if profile_data.updated_at else datetime.now()
            
        db.session.commit()

        return json_response(
            response=ApiResponse.UPDATED_SUCCESSFULLY, 
            data= {"user_profiles": new_profile.to_dict()}
            )

    except IntegrityError as ie:
        db.session.rollback()
        # likely unique/foreign key constraint violation
        current_app.logger.debug("IntegrityError updating users:", ie)
        current_app.logger.debug(traceback.format_exc())
        return json_response(response=ApiResponse.DUPLICATE_ENTRY)
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.debug("Error updating user_profiles:", e)
        current_app.logger.debug(traceback.format_exc())
        return json_response(response=ApiResponse.INTERNAL_ERROR)
    
@user_profiles_bp.route("/l", methods=["POST"])
@firebase_auth_required
def list_users(): 

    try:     
        args = request.get_json() or {}
        current_app.logger.debug("List users request args:", args)
        
        # Get person_uid from query parameters
        uid = args.get("u")
        name = args.get("n")
        org_uid = args.get("o")
        person_uid = args.get("p")
        join_org = args.get("j") # if "j"=1 join organization data in the response
        limit = args.get("limit")  # limit of items per page
        order_by = request.args.get("order")  # field to order by

        join_org = True if join_org in ("1", 1) else False

        user_query = UserProfiles.query

        if (uid is not None and uid != ""):
            user_query = user_query.filter_by(uid=uid)
        else:
            if (org_uid not in ("", None)):
                user_query = user_query.filter_by(default_organization_uid_fk=org_uid)
                if (name not in ("", None)):
                    user_query = user_query.filter(UserProfiles.name.ilike(f"%{name}%"))
                if (person_uid not in ("", None)):
                    user_query = user_query.join(UserProfiles.user_organizations).filter(UserOrganizations.person_uid_fk == person_uid, UserOrganizations.organization_uid_fk == org_uid)
            else:
                return json_response(response=ApiResponse.MISSING_FIELDS)
           
        user_query = user_query.order_by(order_by if order_by is not None else UserProfiles.name.asc())

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", limit if limit is not None else 15))
        pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize data
        data = []
        for user in pagination.items:
            user_data = {}
            user_data["user_profiles"] = user.to_dict(join_org)
           
            data.append(user_data)
        
        return json_response(
            response = ApiResponse.OK,
            data = data,
            total = pagination.total,
            page = pagination.page,
            pages = pagination.pages
        )

    except Exception as e:
        current_app.logger.debug("Error listing users:", e)
        current_app.logger.debug(traceback.format_exc())
        return json_response(response=ApiResponse.INTERNAL_ERROR)

    
@user_profiles_bp.route("/gk", methods=["POST"])
@firebase_auth_required
def getselected_user_keys(): 

    try:     
        args = request.get_json() or {}        
        # Get person_uid from query parameters
        uid = args.get("u")
      
        if (uid is None or uid == ""):
            return json_response(response=ApiResponse.MISSING_FIELDS)

        selected_user_keys = UserKeys.query.get(uid)
        
        return json_response(
            response = ApiResponse.OK,
            data = {"user_keys": selected_user_keys.to_dict() if selected_user_keys else None}
        )

    except Exception as e:
        current_app.logger.debug("Error listing users:", e)
        current_app.logger.debug(traceback.format_exc())
        return json_response(response=ApiResponse.INTERNAL_ERROR)
    
@user_profiles_bp.route("/uk", methods=["POST"])
@firebase_auth_required
def updateselected_user_keys(): 

    try:     
        args = request.get_json() or {}        
        # Get person_uid from query parameters
        uid = args.get("u")
        pin = args.get("p")
        off_pw = args.get("o")
      
        if (uid is None or uid == "") or (pin is None or pin == ""):
            return json_response(response=ApiResponse.MISSING_FIELDS)
        
        _query = UserKeys.query.filter_by(user_profiles_uid_fk=uid)
        selected_user_keys = _query.first()

        if selected_user_keys:
            selected_user_keys.pin_code = UserKeys.bcrypt_hash(pin, uid)
            selected_user_keys.pw_offline = UserKeys.bcrypt_hash(off_pw, uid)
            selected_user_keys.sync_status = "PENDING"
            selected_user_keys.updated_at = datetime.now()
            db.session.commit()
        
        return json_response(
            response = ApiResponse.OK,
            data = {"user_keys": selected_user_keys.to_dict() if selected_user_keys else None}
        )

    except Exception as e:
        current_app.logger.debug("Error updating user keys:", e)
        current_app.logger.debug(traceback.format_exc())
        return json_response(response=ApiResponse.INTERNAL_ERROR)

    
@user_profiles_bp.route("/rk", methods=["POST"])
@firebase_auth_required
def recoverselected_user_keys(): 

    try:     
        args = request.get_json() or {}        
        # Get person_uid from query parameters
        uid = args.get("u")
        email = args.get("e")
        offline_pw = args.get("o") or False
        subject = args.get("s") 
        app_name = args.get("a")

        current_app.logger.debug(f"Recover user keys request received with uid: {uid}, email: {email}, offline_pw: {offline_pw}")
      
        if (uid is None or uid == "") or (email is None or email == "") or (subject is None or subject == "") or (app_name is None or app_name == ""):
            return json_response(response=ApiResponse.MISSING_FIELDS)

        selected_user_keys = UserKeys.query.get(uid)
        if selected_user_keys is None:
            return json_response(response=ApiResponse.NOT_FOUND)

        key6dig = random.randint(100000, 999999)  # Generate a random 6-digit code
        key8dig = random.randint(10000000, 99999999) # Generate a random 8-digit code

        body = f"PIN Code: {key6dig}"
        if offline_pw:
            body += f"\nOffline Password: {key8dig}"

        selected_user_keys.pin_code = UserKeys.bcrypt_hash(key6dig, uid)
        selected_user_keys.pw_offline = UserKeys.bcrypt_hash(key8dig, uid)
        selected_user_keys.sync_status = "PENDING"
        selected_user_keys.updated_at = datetime.now()
        db.session.commit()
            
        smtp_manager = smtp_info()
        send_email_smtp(smtp_manager, service_name=app_name, body=body, subject=subject, receiver_email=email)
       
        return json_response(
            response = ApiResponse.RECOVERY_KEYS_SENT, data = {"user_keys": selected_user_keys.to_dict() if selected_user_keys else None}
        )

    except RuntimeError as e:
        current_app.logger.warning("SMTP recovery failed: %s", e)
        return json_response(response=ApiResponse.EMAIL_FAILED)

    except Exception as e:
        db.session.rollback()
        current_app.logger.debug("Error recovering user keys: %s", e)
        current_app.logger.debug(traceback.format_exc())
        return json_response(response=ApiResponse.INTERNAL_ERROR)
