import uuid
import traceback

from backend.apps.commerciall_api.main import db
from flask import Blueprint, current_app, request
from ...utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required

vehycles_bp = Blueprint("vehycles", __name__)

@vehycles_bp.route("uidr", methods=["POST"])
@firebase_auth_required
def upsert_driver():
    try:
        from ..models.vehycle_models import VehycleDrivers
        data = request.get_json()
        current_app.logger.debug("Received data for upsert:", data)

        _driver = VehycleDrivers.from_json(data)

        if (_driver.organization_uid_fk is None or _driver.organization_uid_fk == "") or (_driver.licence_number is None or _driver.licence_number == ""):
            current_app.logger.debug("Missing required fields: organization_uid_fk or licence_number")
            return json_response(
                response=ApiResponse.MISSING_FIELDS
            )

        _selected = VehycleDrivers.query.filter_by(uid=_driver.uid, organization_uid_fk=_driver.organization_uid_fk).first() if _driver.uid else None

        if _selected:
            for key, value in data.items():
                setattr(_selected, key, value)
            db.session.add(_selected)
            message = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
        else:
            _driver.uid = str(uuid.uuid4())
            db.session.add(_driver)
            message = ApiResponse.CREATED_SUCCESSFULLY
            persisted = _driver

        db.session.commit()

        return json_response(
            response=message,
            data={"driver": persisted.to_dict()}
        )

    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
@vehycles_bp.route("gd", methods=["POST"])
@firebase_auth_required
def get_driver():
    try:
        from ..models.vehycle_models import VehycleDrivers

        data = request.get_json()

        uid = data.get("u")
        person_uid = data.get("pu")
        organization_uid_fk = data.get("o")
    
        if ((uid is None or uid == "") and (person_uid is None or person_uid == "")) or (organization_uid_fk is None or organization_uid_fk == ""):
            return json_response(
                response=ApiResponse.MISSING_FIELDS
            )

        if uid:
            driver = VehycleDrivers.query.filter_by(uid=uid, organization_uid_fk=organization_uid_fk).first()
        else:
            driver = VehycleDrivers.query.filter_by(person_uid_fk=person_uid, organization_uid_fk=organization_uid_fk).first()

        if not driver:
            return json_response(
                response=ApiResponse.NOT_FOUND,
            )

        return json_response(
            response=ApiResponse.OK,
            data={"driver": driver.to_dict()}
        )
    except Exception:
        # Delegate rollback, logging and JSON formatting to Flask's global handlers.
        raise
