import uuid
from .smtp_services import send_email_smtp
from flask import Blueprint, current_app, request
from .smtp_services import send_email_smtp, smtp_info
from ..utils.api_response import ApiResponse, json_response
from ..auth_firebase.firebase_decorators import firebase_auth_required


mail_bp = Blueprint("mail", __name__)

@mail_bp.route("/send", methods=["POST"])
@firebase_auth_required
def send_mail_to_user():

    args = request.get_json()
    uid = args.get("u")
    title = args.get("t")
    body = args.get("m")

    if not uid or not title or not body:
        return json_response(response=ApiResponse.MISSING_FIELDS)
    
    try:
        smtp_manager= smtp_info()
        result = send_email_smtp(smtp_manager, service_name="Notification", body=body, subject=title, receiver_email=None)
        
        if result:
            return json_response(response=ApiResponse.EMAIL_SENT)
        else:
            return json_response(response=ApiResponse.EMAIL_FAILED)
    
    except Exception as e:
        current_app.logger.debug(f"Error sending email: {str(e)}")
        return json_response(response=ApiResponse.EMAIL_FAILED)
