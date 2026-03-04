
from enum import Enum

class ErrorCodes(Enum):
    # Validation errors (2000-2999)
    DUPLICATE_ENTRY = (2000, "Duplicate entry found", 409)
    DUPLICATE_ID_NUMBER = (2001, "ID number already exists", 409)
    DUPLICATE_NAME = (2002, "Name already exists", 409)
    MISSING_FIELDS = (2003, "Required fields are missing", 400)
    INVALID_ENTITY_ID = (2004, "Invalid entity ID", 400)
    
    def __init__(self, code, message, http_status):
        self.code = code
        self.message = message
        self.http_status = http_status

def create_error_response(error_code: ErrorCodes, details=None):
    """Create standardized error response"""
    response_data = {
        "error": {
            "code": error_code.code,
            "message": error_code.message,
            "details": details or {}
        }
    }
    return response_data, error_code.http_status