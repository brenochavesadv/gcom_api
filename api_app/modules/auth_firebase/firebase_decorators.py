import os
from functools import wraps

from flask import current_app, jsonify, request

from .firebase_services import verify_firebase_token


def _is_production_mode():
    """Return True when the app is running in production mode."""
    return os.getenv("FLASK_ENV", current_app.config.get("ENV", "production")) == "production"

def firebase_auth_required(f=None):
    """Decorator to require valid Firebase authentication.

    Supports both usages:
    - @firebase_auth_required
    - @firebase_auth_required()
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # In non-production environments skip strict Firebase auth to ease local testing
            if not _is_production_mode():
                request.firebase_user = None
                current_app.logger.debug("Non-production environment detected, skipping Firebase authentication.")
                return func(*args, **kwargs)

            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'error': 'Authorization header required',
                    'message': 'Please provide Bearer token'
                }), 401

            try:
                token = auth_header.split('Bearer ')[1]
                user_info = verify_firebase_token(token)

                if not user_info:
                    return jsonify({
                        'error': 'Invalid token',
                        'message': 'Token is invalid or expired'
                    }), 401

                request.firebase_user = user_info
                return func(*args, **kwargs)

            except Exception as e:
                return jsonify({
                    'error': 'Authentication failed',
                    'message': str(e)
                }), 401

        return decorated_function

    if f is None:
        return decorator
    else:
        return decorator(f)