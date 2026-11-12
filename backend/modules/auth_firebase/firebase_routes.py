from flask import Blueprint, current_app, request, jsonify

from backend.modules.utils.api_response import ApiResponse, json_response
from .firebase_services import verify_firebase_token, get_user_by_uid, get_user_by_email, notify_user
     
firebase_bp = Blueprint('firebase', __name__)

@firebase_bp.route('/verify-token', methods=['GET'])
def protected():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Missing authorization header'}), 401

    token = auth_header.split('Bearer ')[1]  # Get the actual token part
    decoded_token = verify_firebase_token(token)
    if not decoded_token:
        return jsonify({'error': 'Invalid or revoked token'}), 401

    # Access user data from the decoded token
    user_uid = decoded_token['uid']
    return jsonify({'message': 'Valid token', 'user_uid': user_uid}), 200

@firebase_bp.route('/user', methods=['GET'])
def get_user_info():
    
    uid = request.args.get('u')
    mail = request.args.get('m')
    
    try:
        
        if uid is not None:
            user_info = get_user_by_uid(uid)
        elif mail is not None:
            user_info = get_user_by_email(mail)
        else:
            return json_response(response=ApiResponse.MISSING_FIELDS)

        """
        Get user information by Firebase UID
        """
        
        if user_info:
            return json_response(response=ApiResponse.REQUEST_SUCCESSFUL, data={'user': user_info})
        else:
            return json_response(response=ApiResponse.NOT_FOUND)

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
