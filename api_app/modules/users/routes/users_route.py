import uuid

from main import db
from datetime import datetime
from flask import Blueprint, request, jsonify
from ....constants.response import RESPONSE, json_response
from ..models.users_model import Users
from ..models.user_organizations_model import UserOrganizations
from ..models.users_roles_model import UsersRoles
from ...auth_firebase.firebase_decorators import firebase_auth_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
import traceback
from ..models.organization_model import Organization
from sqlalchemy.orm import contains_eager
from firebase_admin import auth

users_bp = Blueprint("users", __name__)

@users_bp.route("/create", methods=["POST"])
#@firebase_auth_required
def create_users():
    try:
        data = request.get_json() or {}
        user_payload = data.get("user", {})
        user_org_payload = data.get("user_org", {})

        new_user = Users.from_json(user_payload)
        new_user_org = UserOrganizations.from_json(user_org_payload)

        print("Creating user for mail:", new_user.mail)

        if ((new_user.mail is None or new_user.mail == "") 
            or (new_user_org.person_uid_fk is None or new_user_org.person_uid_fk == "") 
            or (new_user_org.organization_uid_fk is None or new_user_org.organization_uid_fk == "")):

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
        new_user_org.users_uid_fk = new_user.uid
        user_exists_in_org = UserOrganizations.query.filter_by(users_uid_fk=new_user_org.users_uid_fk, organization_uid_fk=new_user_org.organization_uid_fk).first()
        person_exists_in_org = UserOrganizations.query.filter_by(person_uid_fk=new_user_org.person_uid_fk, organization_uid_fk=new_user_org.organization_uid_fk).first()

        if user_exists_in_org is not None or person_exists_in_org is not None:
            return json_response(uid=0, response="ALREADY_EXISTS", status_code=409)

        # Upsert local user by Firebase UID.
        user = Users.query.filter_by(uid=new_user.uid).first()
        if user is None:
            user = new_user
            user.uid = firebase_uid
            user.mail = firebase_user.email or new_user.mail
            user.display_name = firebase_user.display_name or new_user.display_name
            user.pin_code = Users.bcrypt_hash('8uaTs', user.uid) if new_user.pin_code else None
            user.pw_offline = Users.bcrypt_hash('84hts', user.uid) if new_user.pw_offline else None
            db.session.add(user)
        else:
            user.mail = new_user.mail or user.mail
            user.name = new_user.name or user.name
            user.display_name = new_user.display_name or user.display_name
            user.location = new_user.location or user.location
            user.language_code = new_user.language_code or user.language_code
            user.iso2_alpha = new_user.iso2_alpha or user.iso2_alpha
            user.date_format = new_user.date_format or user.date_format
            user.pin_code = Users.bcrypt_hash('1hyde', user.uid) if new_user.pin_code else None
            user.pw_offline = Users.bcrypt_hash('1xyTe', user.uid) if new_user.pw_offline else None
            user.default_organization_uid_fk = new_user.default_organization_uid_fk or user.default_organization_uid_fk
            user.sync_status = new_user.sync_status or user.sync_status

        new_user_org.uid = str(uuid.uuid4())
        new_user_org.users_uid_fk = user.uid
        db.session.add(new_user_org)

        db.session.commit()
    
        return json_response(
            uid=user.uid,
            response="CREATED_SUCCESSFULLY",
            status_code=201,
            data={
                "user": f"/users/{user.uid},/user_organizations/{new_user_org.uid}",
                "user_org": {
                    "uid": new_user_org.uid,
                    "users_uid_fk": new_user_org.users_uid_fk,
                    "organization_uid_fk": new_user_org.organization_uid_fk,
                    "person_uid_fk": new_user_org.person_uid_fk,
                    "user_name": new_user_org.user_name,
                },
            },
        )

    except Exception as e:
        print("Error creating user:", e)
        print(traceback.format_exc())
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)


@users_bp.route("/update/<string:upd_type>", methods=["PUT"])
@firebase_auth_required
def update_users(upd_type):
    try:
        user_data = Users.from_json(request.get_json())

        if ((user_data.uid is None or user_data.uid == "") or (user_data.name is None or user_data.name == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        user = Users.query.filter_by(uid=user_data.uid).first()
        if not user:
            return json_response(uid=0, response="NOT_FOUND", status_code=404)

        if upd_type == "u": # update user details
            user.mail = user_data.mail
            user.display_name = user_data.display_name
            user.location = user_data.location
            user.language_code = user_data.language_code
            user.iso2_alpha = user_data.iso2_alpha
            user.state = user_data.state
            user.city = user_data.city
            user.date_format = user_data.date_format
            user.default_organization_uid_fk = user_data.default_organization_uid_fk
            user.is_active = user_data.is_active
        elif upd_type == "o": # update user organizations
            user.user_organizations = user_data.user_organizations
        elif upd_type == "s": # update sync status
            user.sync_status = user_data.sync_status
        elif upd_type == "p": # update pin code
            user.pin_code = Users.bcrypt_hash(user_data.pin_code, user.uid) if user_data.pin_code else None
            user.pin_updated_at = datetime.now()
        else:
            return json_response(uid=0, response="INVALID_UPDATE_TYPE", status_code=400)
            
        db.session.commit()

        return json_response(uid=user.uid, response="UPDATED_SUCCESSFULLY", status_code=200)

    except IntegrityError as ie:
        db.session.rollback()
        # likely unique/foreign key constraint violation
        print("IntegrityError updating users:", ie)
        print(traceback.format_exc())
        return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)
    
    except Exception as e:
        db.session.rollback()
        print("Error updating users:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@users_bp.route("/list", methods=["GET"])
#@firebase_auth_required
def list_users(): 

    try:     
        # Get person_uid from query parameters
        uid = request.args.get("u")
        name = request.args.get("n")
        org_uid = request.args.get("o")
        person_uid = request.args.get("p")
        join_org = request.args.get("j") # if "j"=1 join organization data in the response
        limit = request.args.get("limit")  # limit of items per page
        order_by = request.args.get("order")  # field to order by

        user_query = Users.query

        if (uid is not None and uid != ""):
            user_query = user_query.filter_by(uid=uid)
        else:
            if (org_uid is not None and org_uid != ""):
                user_query = user_query.filter_by(default_organization_uid_fk=org_uid)
                if (name is not None and name != ""):
                    user_query = user_query.filter(Users.name.ilike(f"%{name}%"))
                if (person_uid is not None and person_uid != ""):
                    user_query = user_query.join(Users.user_organizations).filter(UserOrganizations.person_uid_fk == person_uid)
            else:
                return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        """         if join_org is not None and (join_org == "1"):
            join_organization = True
        else:            
            join_organization = False

        if (join_organization): # return json including organization data

                user_query = user_query.join(
                    Organization,
                    Users.default_organization_uid_fk == Organization.uid,
                ).options(contains_eager(Users.organization)) """
           
        user_query = user_query.order_by(order_by if order_by is not None else Users.name.asc())

        # Print runnable SQL for easier copy/paste debugging in DB clients.
        #print(user_query.statement.compile(compile_kwargs={"literal_binds": True}))

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", limit if limit is not None else 15))
        pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize data
        data = []
        for user in pagination.items:
            user_data = {}
            user_data["user"] = user.to_dict(join_orgs=True)
           
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