from flask import Blueprint, request
from ...auth_firebase.firebase_decorators import firebase_auth_required
from ..services.phone_services import phone_list_service, phone_sync_service, phone_upsert_service

phone_bp = Blueprint("phone", __name__)

@phone_bp.route("/ui", methods=["POST"])
@firebase_auth_required
def phone_ui():
        data = request.get_json()
        return phone_upsert_service(data=data)

@phone_bp.route("/list", methods=["POST"])
@firebase_auth_required
def phone_list():
    data = request.get_json()
    return phone_list_service(data=data)

    
@phone_bp.route("/sync", methods=["GET"])
@firebase_auth_required
def phone_sync():
    data = request.get_json()
    return phone_sync_service(data=data)
