

from ..docs.person import person_docs
from ..services.person_services import person_list, person_upsert
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from flask import Blueprint, request

person_bp = Blueprint("person", __name__)


def get_person(data=None):
    """Backward-compatible service entry point for related person services."""
    return person_list(data=data or {})

@person_bp.route("/list", methods=["POST"])
@firebase_auth_required
@swag_from(person_docs["person_list"])
def route_person_list():
    data = request.get_json()
    return person_list(data=data)

@person_bp.route("/ui", methods=["POST"])
@firebase_auth_required
@swag_from(person_docs["person_ui"])
def route_person_ui():
    data = request.get_json()
    return person_upsert(data=data)
