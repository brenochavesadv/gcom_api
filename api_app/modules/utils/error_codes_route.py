from flask import Blueprint, jsonify
from flasgger import swag_from
from .error_codes import ErrorCodes
from ..auth_firebase.firebase_decorators import firebase_auth_required

errors_bp = Blueprint("errors", __name__)

@errors_bp.route("/", methods=["GET"])
@firebase_auth_required
@swag_from({
    'tags': ['Errors'],
    'parameters': [],
    'responses': {
        200: {
            'description': 'Lista de erros para retorno'
        }
    }
})

def list_errors():
    try:
        data = [ErrorCodes.create_error_response(error_code) for error_code in ErrorCodes.__members__.values()]
        return jsonify({
            "items": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
       