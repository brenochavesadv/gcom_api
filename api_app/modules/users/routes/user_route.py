import uuid

from main import db
from datetime import datetime
from flask import Blueprint, request, jsonify
from ....constants.response import RESPONSE, json_response
from ..models.user_profiles_model import UserProfiles   
from ..models.user_organizations_model import UserOrganizations
from ..models.user_roles_model import UserRoles
from ..models.user_keys_model import UserKeys
from ...auth_firebase.firebase_decorators import firebase_auth_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
import traceback
from ..models.organization_model import Organization
from sqlalchemy.orm import contains_eager
from firebase_admin import auth

users_bp = Blueprint("users", __name__)

# creates new user on UserOrganizations and UserProfiles
@users_bp.route("/create", methods=["POST"])
#@firebase_auth_required
def create_users():
    try:
        data = request.get_json() or {}
        user_payload = data.get("user_profiles", {})
        user_org_payload = data.get("user_organizations", {})
        print("user_payload:", user_payload)
        print("user_org_payload:", user_org_payload)

        new_user = UserProfiles.from_json(user_payload)
        new_user_org = UserOrganizations.from_json(user_org_payload)

        print("Creating user for mail:", new_user.mail)

        if ((new_user.mail is None or new_user.mail == "") 
            or (new_user_org.person_uid_fk is None or new_user_org.person_uid_fk == "") 
            or (new_user_org.organization_uid_fk is None or new_user_org.organization_uid_fk == "")
            or (new_user_org.user_name is None or new_user_org.user_name == "")):

            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        # Resolve UID from Firebase: reuse existing user by email, otherwise create.
        try:
            
            firebase_user = auth.get_user_by_email(new_user.mail)
            firebase_uid = firebase_user.uid
            print(f"Firebase user {firebase_user.email} found with UID: {firebase_uid}")
            
        except auth.UserNotFoundError:
            
            if not new_user.uid:
                new_user.uid = str(uuid.uuid4())
                
            firebase_user = auth.create_user(
                uid=new_user.uid,
                email=new_user.mail,
                display_name=new_user.display_name,
            )
            
            firebase_uid = firebase_user.uid
            print(f"Firebase user created for {new_user.mail} with UID: {firebase_uid}")

        new_user.uid = firebase_uid

        # Validate duplicate membership in organization.
        new_user_org.user_profiles_uid_fk = new_user.uid
        user_exists_in_org = UserOrganizations.query.filter_by(user_profiles_uid_fk=new_user.uid, organization_uid_fk=new_user_org.organization_uid_fk).first()
        person_exists_in_org = UserOrganizations.query.filter_by(person_uid_fk=new_user_org.person_uid_fk, organization_uid_fk=new_user_org.organization_uid_fk).first()

        if user_exists_in_org is not None or person_exists_in_org is not None:
            return json_response(uid=0, response="ALREADY_EXISTS", status_code=409)

        # Upsert local user by Firebase UID.
        user = UserProfiles.query.filter_by(uid=new_user.uid).first()
        user_keys = ''
        
        if user is None:
            user = new_user
            user.uid = firebase_uid
            user.mail = firebase_user.email or new_user.mail
            user.display_name = firebase_user.display_name or new_user.display_name

            db.session.add(user)

            user_keys = UserKeys(
                uid=str(uuid.uuid4()),
                user_profiles_uid_fk=user.uid,
                pin_code=UserKeys.bcrypt_hash(str(uuid.uuid4()), user.uid),
                pw_offline=UserKeys.bcrypt_hash(str(uuid.uuid4()), user.uid),
            )
            
            db.session.add(user_keys)
        else:
            user.mail = new_user.mail or user.mail
            user.name = new_user.name or user.name
            user.display_name = new_user.display_name or user.display_name
            user.location = new_user.location or user.location
            user.language_code = new_user.language_code or user.language_code
            user.iso2_alpha = new_user.iso2_alpha or user.iso2_alpha
            user.date_format = new_user.date_format or user.date_format
            user.default_organization_uid_fk = new_user.default_organization_uid_fk or user.default_organization_uid_fk
            user.sync_status = new_user.sync_status or user.sync_status

        new_user_org.uid = str(uuid.uuid4())
        new_user_org.user_profiles_uid_fk = user.uid
        db.session.add(new_user_org)

        db.session.commit()

        return_data = {}
        return_data["user_profiles"] = user.to_dict()
        return_data["user_profiles"]["user_keys"] = [user_keys.to_dict() if user_keys else None]
        return_data["user_profiles"]["user_organizations"] = [new_user_org.to_dict()]
        
        print("User created successfully! return_data: ", return_data)

        return json_response(
            uid=user.uid,
            response="CREATED_SUCCESSFULLY",
            status_code=201,
            data= return_data            
        )

    except Exception as e:
        print("Error creating user:", e)
        print(traceback.format_exc())
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)


# update user_organizations_model
@users_bp.route("/update", methods=["PUT"])
#@firebase_auth_required
def update_user_organizations():
    try:
        data = request.get_json() or {}
        user_org_payload = data.get("user_organizations", {})

        new_user_org = UserOrganizations.from_json(user_org_payload)

        if ((new_user_org.uid is None or new_user_org.uid == "") 
            or (new_user_org.allowed_app_routes is None or new_user_org.allowed_app_routes == "") 
            or (new_user_org.user_roles_uid_fk is None or new_user_org.user_roles_uid_fk == "")):

            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        # Resolve UID from Firebase: reuse existing user by email, otherwise create.
        
        user_org = UserOrganizations.query.filter_by(uid=new_user_org.uid).first()

        if user_org is None:
            return json_response(uid=0, response="NOT FOUND", status_code=400)  

        user_org.user_roles_uid_fk = new_user_org.user_roles_uid_fk or user_org.user_roles_uid_fk
        user_org.is_active = new_user_org.is_active if new_user_org.is_active is not None else user_org.is_active
        user_org.sync_status = "PENDING"
        user_org.allowed_app_routes = new_user_org.allowed_app_routes or user_org.allowed_app_routes
        user_org.updated_at = datetime.now()
            
        db.session.commit()

        return json_response(
            uid=user_org.uid,
            response="CREATED_SUCCESSFULLY",
            status_code=201,
            data= {"user_organizations": user_org.to_dict()}
        )

    except Exception as e:
        print("Error creating user:", e)
        print(traceback.format_exc())
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)

    
@users_bp.route("/profile", methods=["PUT"])
#@firebase_auth_required
def update_profile():
    try:
        data = request.get_json() or {}         
        profile_data = UserProfiles.from_json(data.get("user_profiles", {}))

        if ((profile_data.uid is None or profile_data.uid == "") 
            or (profile_data.display_name is None or profile_data.display_name == "")):   
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        new_profile = UserProfiles.query.filter_by(uid=profile_data.uid).first()
        if not new_profile:
            return json_response(uid=0, response="NOT_FOUND", status_code=404)

        new_profile.display_name = profile_data.display_name
        new_profile.location = profile_data.location
        new_profile.language_code = profile_data.language_code
        new_profile.iso2_alpha = profile_data.iso2_alpha
        new_profile.date_format = profile_data.date_format
        new_profile.default_organization_uid_fk = profile_data.default_organization_uid_fk
        new_profile.updated_at = profile_data.updated_at if profile_data.updated_at else datetime.now()
            
        db.session.commit()

        return json_response(
            uid=new_profile.uid, 
            response="UPDATED_SUCCESSFULLY", 
            status_code=200,
            data= {"user_profiles": new_profile.to_dict()}
            )

    except IntegrityError as ie:
        db.session.rollback()
        # likely unique/foreign key constraint violation
        print("IntegrityError updating users:", ie)
        print(traceback.format_exc())
        return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)
    
    except Exception as e:
        db.session.rollback()
        print("Error updating user_profiles:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@users_bp.route("/list", methods=["POST"])
#@firebase_auth_required
def list_users(): 

    try:     
        args = request.get_json() or {}
        print("List users request args:", args)
        
        # Get person_uid from query parameters
        uid = args.get("u")
        name = args.get("n")
        org_uid = args.get("o")
        person_uid = args.get("p")
        join_org = args.get("j") # if "j"=1 join organization data in the response
        limit = args.get("limit")  # limit of items per page
        order_by = request.args.get("order")  # field to order by

        user_query = UserProfiles.query

        if (uid is not None and uid != ""):
            user_query = user_query.filter_by(uid=uid)
        else:
            if (org_uid is not None and org_uid != ""):
                user_query = user_query.filter_by(default_organization_uid_fk=org_uid)
                if (name is not None and name != ""):
                    user_query = user_query.filter(UserProfiles.name.ilike(f"%{name}%"))
                if (person_uid is not None and person_uid != ""):
                    user_query = user_query.join(UserProfiles.user_organizations).filter(UserOrganizations.person_uid_fk == person_uid)
            else:
                return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        """         if join_org is not None and (join_org == "1"):
            join_organization = True
        else:            
            join_organization = False

        if (join_organization): # return json including organization data

                user_query = user_query.join(
                    Organization,
                    UserProfiles.default_organization_uid_fk == Organization.uid,
                ).options(contains_eager(UserProfiles.organization)) """
           
        user_query = user_query.order_by(order_by if order_by is not None else UserProfiles.name.asc())

        # Print runnable SQL for easier copy/paste debugging in DB clients.
        #print(user_query.statement.compile(compile_kwargs={"literal_binds": True}))

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", limit if limit is not None else 15))
        pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize data
        data = []
        for user in pagination.items:
            user_data = {}
            user_data["user_profiles"] = user.to_dict(join_orgs=True)
           
            data.append(user_data)
        
        return json_response(
            response = "OK",
            status_code = 200,
            data = data,
            total = pagination.total,
            page = pagination.page,
            pages = pagination.pages
        )

    except Exception as e:
        print("Error listing users:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)

    
@users_bp.route("/gk", methods=["POST"])
#@firebase_auth_required
def get_user_keys(): 

    try:     
        args = request.get_json() or {}        
        # Get person_uid from query parameters
        uid = args.get("u")
      
        if (uid is None or uid == ""):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        _user_keys = UserKeys.query.get(uid)
        
        return json_response(
            response = "OK",
            status_code = 200,
            data = {"user_keys": _user_keys.to_dict() if _user_keys else None}
        )

    except Exception as e:
        print("Error listing users:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)

    
@users_bp.route("/uk", methods=["PUT"])
#@firebase_auth_required
def update_user_keys(): 

    try:     
        args = request.get_json() or {}        
        # Get person_uid from query parameters
        uid = args.get("u")
        pin = args.get("p")
        pw = args.get("pw")
      
        if (uid is None or uid == "") or (pin is None or pin == "") or (pw is None or pw == ""):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        _query = UserKeys.query.filter_by(user_profiles_uid_fk=uid)
        _user_keys = _query.first()

        if _user_keys:
            _user_keys.pin_code = UserKeys.bcrypt_hash(pin, uid)
            _user_keys.pw_offline = UserKeys.bcrypt_hash(pw, uid)
            _user_keys.sync_status = "PENDING"
            _user_keys.updated_at = datetime.now()
            db.session.commit()
        
        return json_response(
            response = "OK",
            status_code = 200,
            data = {"user_keys": _user_keys.to_dict() if _user_keys else None}
        )

    except Exception as e:
        print("Error updating user keys:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)