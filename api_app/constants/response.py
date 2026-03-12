from flask import jsonify

RESPONSE = {
    "OK": { 'code': 200, 'message': "OK" },
    "MISSING_FIELDS": { 'code': 2003 , 'message': "Missing required fields" },
    "NOT_FOUND": { 'code': 2004, 'message': "Resource not found" },
    "DB_CONFLICT": { 'code': 2005, 'message': "Database conflict" },
    "UNAUTHORIZED": { 'code': 2006, 'message': "Unauthorized" },
    "INTERNAL_ERROR": { 'code': 5000, 'message': "Internal server error" },
    "DUPLICATE_ENTRY": { 'code': 2007, 'message': "Duplicate entry" },
    "SAVED_SUCCESSFULLY": { 'code': 200, 'message': "Saved successfully" },
    "UPDATED_SUCCESSFULLY": { 'code': 200, 'message': "Updated successfully" },
    "CREATED_SUCCESSFULLY": { 'code': 201, 'message': "Created successfully" },
    "ONE_MAIN_REQUIRED": { 'code': 2008, 'message': "At least one main is required" },
}

def json_response(response, status_code, uid='', data=None, total=0, page=0, pages=0):
    return jsonify({
        "uid": uid,
        "response": response,
        "message": RESPONSE[response]['message'] if response in RESPONSE else "",
        "response_code": RESPONSE[response]['code'] if response in RESPONSE else 0,
        "data": data,
        "total": total,
        "page": page,
        "pages": pages
    }), status_code     