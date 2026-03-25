from main import db
from datetime import datetime
from flask import Blueprint, request, jsonify
from ...constants.response import RESPONSE, json_response
from ..auth_firebase.firebase_decorators import firebase_auth_required
from sqlalchemy.exc import IntegrityError
import traceback
from .sync_queue_model import SyncQueue

sync_bp = Blueprint("sync", __name__)

""" @sync_bp.route("/update/<string:upd_type>", methods=["PUT"])
@firebase_auth_required
def update_sync(upd_type):
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
        elif upd_type == "r": # update permissions (roles)
            user.permissions = user_data.permissions
        elif upd_type == "o": # update user organizations
            user.user_organizations = user_data.user_organizations
        elif upd_type == "s": # update sync status
            user.sync_status = user_data.sync_status
        elif upd_type == "g": # update users group
            user.users_group_uid_fk = user_data.users_group_uid_fk
            user.permissions = user_data.permissions
        elif upd_type == "p": # update pin code
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
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500) """
    
@sync_bp.route("/last", methods=["GET"])
#@firebase_auth_required
def list_users(): 

    try:     
        org_uid = request.args.get("o")
        table = request.args.get("t")

        if (table is None or table == ""):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        sync_query = SyncQueue.query.filter_by(operation_table=table)

        if (table != "app_routes"):
            if (org_uid is None or org_uid == ""):
                return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
            else:
                sync_query = sync_query.filter_by(organization_uid_fk=org_uid)
        
        # Serialize data
        data = []
        for sync_item in sync_query.all():
            data.append(sync_item.to_dict())
        
        return json_response(
            response = "OK",
            status_code = 200,
            data = data,
            total = len(data),
            page = 1,
            pages = 1
        )

    except Exception as e:
        print("Error listing users:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)