from flask import Blueprint, request, jsonify
from .firebase import verify_firebase_token, get_user_by_uid
     
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
    user_id = decoded_token['uid']
    return jsonify({'message': 'Valid token', 'user_id': user_id}), 200

@firebase_bp.route('/user/<uid>', methods=['GET'])
def get_user_info(uid):
    """
    Get user information by Firebase UID
    """
    try:
        user_info = get_user_by_uid(uid)
        
        if user_info:
            return jsonify({
                'success': True,
                'user': user_info
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500