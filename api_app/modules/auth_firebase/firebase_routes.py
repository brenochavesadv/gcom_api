from flask import Blueprint, request, jsonify

from api_app.constants.response import json_response
from .firebase_services import verify_firebase_token, get_user_by_uid, get_user_by_email
     
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
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        """
        Get user information by Firebase UID
        """
        
        if user_info:
            return json_response(uid=1, response="OK", status_code=200, data={'user': user_info})
        else:
            return json_response(uid=0, response="USER_NOT_FOUND", status_code=404)

    except Exception as e:
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)