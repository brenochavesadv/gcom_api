

from ..docs.person import person_docs
from ..services.person_services import get_person
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from flask import Blueprint, request

person_bp = Blueprint("person", __name__)

@person_bp.route("/list", methods=["POST"])
@firebase_auth_required
@swag_from(person_docs["list_person"])
def list_person():
    data = request.get_json()
    return get_person(data=data)