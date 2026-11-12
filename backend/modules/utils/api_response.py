from http import HTTPStatus
from typing import Any, Dict, Optional, Union
from flask import current_app, jsonify
from enum import Enum


class ApiResponse(Enum):
    """Application responses carrying an application code, HTTP status and message.

    Members are defined as: (app_code, http_status, message)
    - `app_code` is an internal numeric code used inside the JSON payload.
    - `http_status` is a valid HTTP status code returned by the endpoint.
    - `message` is a human-readable description.
    """

    MISSING_FIELDS = (2003, 400, "Missing required fields")
    NOT_FOUND = (2004, 404, "Resource not found")
    DB_CONFLICT = (2005, 409, "Database conflict")
    INTERNAL_ERROR = (5000, 500, "Internal server error")
    DUPLICATE_ENTRY = (2007, 409, "Duplicate entry")
    UPSERTED_SUCCESSFULLY = (201, 201, "upserted successfully")
    SAVED_SUCCESSFULLY = (200, 200, "Saved successfully")
    UPDATED_SUCCESSFULLY = (200, 200, "Updated successfully")
    CREATED_SUCCESSFULLY = (201, 201, "Created successfully")
    OK = (200, 200, "OK")
    NO_DATA = (204, 204, "No data")
    NO_DATA_UPDATED = (204, 204, "No data updated")
    REQUEST_SUCCESSFUL = (200, 200, "Request successful")
    EMAIL_SENT = (200, 200, "Email sent successfully")
    EMAIL_FAILED = (500, 500, "Failed to send email")
    RECOVERY_KEYS_SENT = (200, 200, "Recovery keys sent to email if user exists")
    ALREADY_EXISTS = (4091, 409, "Already exists")
    INVALID_UPDATE_TYPE = (4001, 400, "Invalid update type")
    VEHYCLE_NOT_FOUND = (4042, 404, "Vehycle not found")
    ONE_MAIN_REQUIRED = (2008, 400, "At least one main is required")
    VALIDATION_ERROR = (4220, 422, "Validation error")
    METHOD_NOT_ALLOWED = (4050, 405, "Method not allowed")
    FORBIDDEN = (4030, 403, "Forbidden")
    BAD_REQUEST = (4000, 400, "Bad request: invalid data or missing fields")
    CONFLICT = (4090, 409, "Conflict")
    UNPROCESSABLE_ENTITY = (4221, 422, "Unprocessable entity")
    UNAUTHORIZED = (4010, 401, "Unauthorized: authentication required or failed")
    BAD_GATEWAY = (5020, 502, "Bad gateway: server acting as gateway received invalid response")
    SERVICE_UNAVAILABLE = (5030, 503, "Service unavailable: server temporarily unavailable (maintenance or overload)")
    GATEWAY_TIMEOUT = (5040, 504, "Gateway timeout: server acting as gateway did not receive timely response")
    REQUEST_TIMEOUT = (4080, 408, "Request timeout: server did not receive complete request within timeout period")

    def __init__(self, app_code: int, http_status: int, message: str):
        self._app_code = app_code
        self._http_status = http_status
        self._message = message

    @property
    def app_code(self) -> int:
        return self._app_code

    @property
    def http_status(self) -> int:
        return self._http_status

    @property
    def message(self) -> str:
        return self._message


def json_response(
    response: Union[ApiResponse, str],
    data: Optional[Any] = None,
    total: int = 0,
    page: int = 0,
    pages: int = 0,
    exception: Optional[Exception] = None,
):
    
    """Return a Flask JSON response using a `ApiResponse` definition.

    Accepts either a `ApiResponse` or the enum name as a `str`.
    The response payload includes an `app_code` (internal) while the HTTP
    status code returned uses a valid `http_status`.
    """
    if isinstance(response, str):
        try:
            response = ApiResponse[response]
        except KeyError:
            response = ApiResponse.INTERNAL_ERROR

    if exception:
        import traceback
        current_app.logger.error(f"Exception occurred: {exception}")
        current_app.logger.error(traceback.format_exc())

    exception_name = (
        type(exception).__name__
        if isinstance(exception, BaseException)
        else str(exception) if exception is not None else None
    )

    status_message = HTTPStatus(response.http_status).phrase if response.http_status in HTTPStatus._value2member_map_ else "Unknown Status"

    body = {
        "statusCode": response.http_status,
        "statusMessage": status_message,
        "message": response.message,
        "response": response.name,
        "data": data,
        "extra": {
            "total": total,
            "page": page,
            "pages": pages,
            "appCode": response.app_code,
            "exception": exception_name,
        },
    }

    return jsonify(body), response.http_status

def extract_data(result, key):
    response = result[0] if isinstance(result, tuple) else result
    payload = response.get_json() if hasattr(response, "get_json") else {}
    if not isinstance(payload, dict):
        payload = {}
    data = payload.get("data")
    if not isinstance(data, dict):
        return {}
    return data.get(key, {})
