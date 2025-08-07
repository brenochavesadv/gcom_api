import firebase_admin
from firebase_admin import credentials, auth
import os

# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "firebase_config.json")

cred = credentials.Certificate(config_path)
firebase_app = firebase_admin.initialize_app(cred)

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
    except auth.UserNotFoundError:
        print(f"User with UID {uid} not found")
        return None
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None
