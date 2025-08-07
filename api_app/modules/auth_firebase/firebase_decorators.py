from functools import wraps
from flask import request, jsonify
from .firebase import verify_firebase_token

def auth_required(f):
    """
    Decorator to require valid Firebase authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Authorization header required',
                'message': 'Please provide Bearer token'
            }), 401
        
        try:
            # Extract token
            token = auth_header.split('Bearer ')[1]
            user_info = verify_firebase_token(token)
            
            if not user_info:
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'Token is invalid or expired'
                }), 401
            
            # Add user info to request context
            request.firebase_user = user_info
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'error': 'Authentication failed',
                'message': str(e)
            }), 401
    
    return decorated_function