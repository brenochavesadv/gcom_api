from main import db
from datetime import datetime
from flask import Blueprint, request, jsonify
from ....constants.response import RESPONSE, json_response
from ..models.users_model import Users
from ...auth_firebase.firebase_decorators import firebase_auth_required
from sqlalchemy.exc import IntegrityError
import traceback
from ..models.organization_model import Organization
from sqlalchemy.orm import contains_eager

users_bp = Blueprint("users", __name__)

@users_bp.route("/create", methods=["POST"])
@firebase_auth_required
def create_users():
    try:
        user = Users.from_json(request.get_json())
        
        if ((user.uid is None or user.uid == "") or (user.email is None or user.email == "") or (user.name is None or user.name == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        if Users.query.filter_by(uid=user.uid).first():
            return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

        new_user = Users(
            uid=user.uid,
            mail=user.mail,
            name=user.name,
            display_name=user.display_name,
            login=user.login,
            location=user.location,
            language_code=user.language_code,
            iso2_alpha=user.iso2_alpha,
            state=user.state,
            city=user.city,
            date_format=user.date_format,
            pin_code=user.pin_code,
            pin_updated_at=user.pin_updated_at,
            is_developer=user.is_developer,
            default_organization_uid_fk=user.default_organization_uid_fk,
            is_active=user.is_active,
            login_counter=user.login_counter,
            users_group_uid_fk=user.users_group_uid_fk,
            permissions=user.permissions,
            user_organizations=user.user_organizations,
            sync_status=user.sync_status,
        )

        db.session.add(new_user)
        db.session.commit()
    
        return json_response(uid=new_user.uid, response="CREATED_SUCCESSFULLY", status_code=201)

    except Exception as e:
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)


@users_bp.route("/update/<string:type>", methods=["PUT"])
@firebase_auth_required
def update_users():
    try:
        user_data = Users.from_json(request.get_json())

        if ((user_data.uid is None or user_data.uid == "") or (user_data.name is None or user_data.name == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        user = Users.query.filter_by(uid=user_data.uid).first()
        if not user:
            return json_response(uid=0, response="NOT_FOUND", status_code=404)

        if type == "u": # update user details
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
        elif type == "r": # update permissions (roles)
            user.permissions = user_data.permissions
        elif type == "o": # update user organizations
            user.user_organizations = user_data.user_organizations
        elif type == "s": # update sync status
            user.sync_status = user_data.sync_status
        elif type == "g": # update users group
            user.users_group_uid_fk = user_data.users_group_uid_fk
            user.permissions = user_data.permissions
        elif type == "p": # update pin code
            user.pin_code = user_data.pin_code
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
        join_org = request.args.get("j") # if "j"=1 join organization data in the response
        limit = request.args.get("limit")  # limit of items per page
        order_by = request.args.get("order")  # field to order by

        user_query = Users.query

        if (uid is not None and uid != ""):
            print("Fetching users by uid:", uid)
            user_query = user_query.filter_by(uid=uid)
        elif (org_uid is not None and org_uid != ""):
            print("Fetching users by org_uid:", org_uid)
            user_query = user_query.filter_by(default_organization_uid_fk=org_uid)
        elif (name is not None and name != ""):
            print("Fetching users by name:", name)
            user_query = user_query.filter(Users.name.ilike(f"%{name}%"))
        else:
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        if join_org is not None and (join_org == "1"):
            join_organization = True
        else:            
            join_organization = False

        print("Join Organization:", join_organization)

        if (join_organization): # return json including organization data
            user_query = user_query.join(
                Organization,
                Users.default_organization_uid_fk == Organization.uid,
            ).options(contains_eager(Users.organization))

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
            user_data["user"] = user.to_dict()
            if join_organization and user.organization:
                user_data["user"]["organization"] = user.organization.to_dict()
           
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