import uuid
from .smtp_services import send_email_smtp
from flask import Blueprint, request
from .smtp_services import send_email_smtp, smtp_info
from ...constants.response import RESPONSE, json_response

mail_bp = Blueprint("mail", __name__)

@mail_bp.route("/send", methods=["POST"])
#@firebase_auth_required
def send_mail_to_user():

    args = request.get_json()
    uid = args.get("u")
    title = args.get("t")
    body = args.get("m")

    if not uid or not title or not body:
        return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
    
    try:
        smtp_info = smtp_info()
        result = send_email_smtp(smtp_info, service_name="Notification", body=body, subject=title, receiver_email=None)
        
        if result:
            return json_response(uid=1, response="EMAIL_SENT", status_code=200)
        else:
            return json_response(uid=0, response="EMAIL_FAILED", status_code=500)
    
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return json_response(uid=0, response="EMAIL_ERROR", status_code=500)
