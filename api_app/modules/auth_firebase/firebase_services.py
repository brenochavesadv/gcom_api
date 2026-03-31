import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, auth, messaging
from flask import current_app

def init_app(app):
    """Initialize Firebase admin SDK using Flask `app` config or environment."""

    creds = None
    cred_json = os.environ.get("INFO_FIREBASE")
    cred_b64 = os.environ.get("FIREBASE_COMMERCIAL_B64")

    if cred_json:
        cred_json_path = os.path.expanduser(cred_json)
        cred_json_path = os.path.abspath(cred_json_path)
        if os.path.exists(cred_json_path):
            with open(cred_json_path, "r", encoding="utf-8") as f:
                creds = json.load(f)
        else:
            try:
                creds = json.loads(cred_json)
            except Exception:
                creds = None

    if creds is None and cred_b64:
        try:
            decoded = base64.b64decode(cred_b64)
            creds = json.loads(decoded)
        except Exception:
            creds = None

    if creds is None:
        raise RuntimeError("Firebase credentials not found.")

    # Extract project_id and set GOOGLE_CLOUD_PROJECT if missing
    project_id = creds.get("project_id") if isinstance(creds, dict) else None
    if project_id:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)

    # Initialize firebase admin if not already
    try:
        firebase_admin.get_app()
    except ValueError:
        try:
            cred = credentials.Certificate(creds)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Firebase admin SDK: {e}")

def verify_firebase_token(id_token):
    """
    Verify Firebase ID token and return user info
    
    Args:
        id_token (str): Firebase ID token from client
        
    Returns:
        dict: User information if token is valid
        None: If token is invalid
    """
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        
        # Extract user information
        user_info = {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            'email_verified': decoded_token.get('email_verified', False),
            'name': decoded_token.get('name'),
            'picture': decoded_token.get('picture'),
            'firebase_claims': decoded_token
        }
        
        return user_info
        
    except auth.InvalidIdTokenError:
        print("Invalid ID token")
        return None
    except auth.ExpiredIdTokenError:
        print("Token has expired")
        return None
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return None

def get_user_by_uid(uid):
    """
    Get user information by UID
    
    Args:
        uid (str): Firebase user UID
        
    Returns:
        dict: User information if user exists
        None: If user doesn't exist
    """
    try:
        user_record = auth.get_user(uid)
        return user_to_dict(user_record)
    except auth.UserNotFoundError:
        print(f"User with UID {uid} not found")
        return None
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None

def user_to_dict(user_record):
    """
    Convert Firebase user record to dictionary format
    
    Args:
        user_record (firebase_admin.auth.UserRecord): Firebase user record
        
    Returns:
        dict: User information in dictionary format
    """
    return {
        'uid': user_record.uid,
        'email': user_record.email,
        'email_verified': user_record.email_verified,
        'display_name': user_record.display_name,
        'photo_url': user_record.photo_url,
        'disabled': user_record.disabled,
        'creation_time': user_record.user_metadata.creation_timestamp,
        'last_sign_in': user_record.user_metadata.last_sign_in_timestamp
    }
