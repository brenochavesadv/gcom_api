import random
import uuid
import traceback

import requests
from flask_sqlalchemy import pagination
from sqlalchemy import or_

from api_app.modules.person.models.person_model import Person
from main import db
from flask import Blueprint, request
from ...constants.response import RESPONSE, json_response
from ..auth_firebase.firebase_decorators import firebase_auth_required
from .models.vehycle_models import VehyclesTypes

vehycles_bp = Blueprint("vehycles", __name__)

@vehycles_bp.route("ufb", methods=["GET"])
#@firebase_auth_required
def update_fipe_brands():
    try:
        from .services.fipe_parallelum_services import update_all_fipe_brands
        data = update_all_fipe_brands()

        if data is None:
            return json_response(
                response="NO_DATA_UPDATED",
                status_code=500,
                data=[]
            )

        return json_response(
            response="UPDATED_SUCCESSFULLY",
            status_code=201,
            data={"fipe_brands": data}
        )

    except requests.RequestException as e:
        print("FIPE request failed:", e)
        print(traceback.format_exc())
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=502)
    except ValueError as e:
        print("Invalid parameters for FIPE years:", e)
        return json_response(response="MISSING_FIELDS", status_code=400, data=[])
    except Exception as e:
        print("Error creating user:", e)
        print(traceback.format_exc())
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)


@vehycles_bp.route("ufvy", methods=["GET"])
#@firebase_auth_required
def update_fipe_vehycles_years():

    vehycle_type = (request.args.get("t") or "").lower()
    fipe_brand_code = (request.args.get("b") or "").lower()
    fipe_vehycle_code = (request.args.get("v") or "").lower()

    print(f"Received parameters - Type: {vehycle_type}, Brand Code: {fipe_brand_code}, Vehycle Code: {fipe_vehycle_code}")

    if not fipe_brand_code or not vehycle_type or not fipe_vehycle_code:
        return json_response(
            response="MISSING_FIELDS",
            status_code=400,
            data=[]
        )

    try:
        from .services.fipe_parallelum_services import fetch_fipe_years_by_model
        data = fetch_fipe_years_by_model(vehycle_type, fipe_brand_code, fipe_vehycle_code)

        if data is None:
            return json_response(
                response="NO_DATA_UPDATED",
                status_code=500,
                data=[]
            )

        return json_response(
            response="UPDATED_SUCCESSFULLY",
            status_code=201,
            data={"fipe_vehycle": data}
        )

    except requests.RequestException as e:
        print("FIPE request failed:", e)
        print(traceback.format_exc())
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=502)
    except Exception as e:
        print("Error creating user:", e)
        print(traceback.format_exc())
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)

@vehycles_bp.route("fvfb", methods=["GET"])
#@firebase_auth_required
def fipe_vehycles_from_brand():
    try:
        vehycle_type = (request.args.get("t") or "").lower()
        fipe_brand_code = (request.args.get("b") or "").lower()
        
        if not fipe_brand_code or not vehycle_type:
            return json_response(
                response="MISSING_FIELDS",
                status_code=400,
                data=[]
            )

        try:
            _type = VehyclesTypes(vehycle_type)
        except ValueError:
            return json_response(
                response="MISSING_FIELDS",
                status_code=400,
                data=[]
            )

        from .models.fipe_models import FipeSyncControl
        last_update = db.session.query(FipeSyncControl).filter_by(vehycle_brand=fipe_brand_code,type=_type.value).order_by(FipeSyncControl.vehycle_brand_last_update_at.desc()).first()

        from datetime import datetime, timedelta
        
        if last_update is None:
            time_diff = timedelta(days=9999)  # Force update if no record exists
        else:
            time_diff = datetime.now() - last_update.vehycle_brand_last_update_at
            
        if time_diff < timedelta(days=25):
            print(f"Using cached data for brand {fipe_brand_code} and type {_type.value}, last updated at {last_update.vehycle_brand_last_update_at}")
            from .models.fipe_models import FipeVehycle
            vehycles = FipeVehycle.query.filter_by(fipe_brand_code_fk=fipe_brand_code, type=_type.value).order_by(FipeVehycle.name).all()
            data = [vehycle.to_dict() for vehycle in vehycles]

        else:
            print(f"Fetching new data for brand {fipe_brand_code} and type {_type.value} from FIPE API")
            from .services.fipe_parallelum_services import update_fipe_vehycles_from_brand
            data = update_fipe_vehycles_from_brand(fipe_brand_code, _type)

        if not data:
            return json_response(
                response="NO_DATA",
                status_code=500,
                data=[]
            )

        return json_response(
                response="OK",
                status_code=200,
                data={"fipe_vehycles": data}
            )

    except Exception as e:
        print("Error creating user:", e)
        print(traceback.format_exc())
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@vehycles_bp.route("lr", methods=["POST"])
#@firebase_auth_required
def list_registered():
    try:
        from .models.vehycle_models import Vehycles
        data = request.get_json()
        print("Received data:", data)
        o = data.get("o")
        np = data.get("np") # nickname or plate
        name = data.get("name")
        order = data.get("order")
        page = data.get("page",1) 
        limit = data.get("limit", 10)

        if (o is None or o == ""):
            return json_response(
                response="MISSING_FIELDS",
                status_code=400,
                data=[]
            )
            
        _query = Vehycles.query.filter_by(organization_uid_fk=o)

        if (np is not None and np != ""):
            _query = _query.filter(
                or_(
                    Vehycles.nickname.ilike(f"%{np}%"),
                    Vehycles.plate.ilike(f"%{np}%")
                )
            )
        elif(name is not None and name != ""):
            _query = _query.filter(Vehycles.name.ilike(f"%{name}%"))

        order_column = getattr(Vehycles, order, None)
        if order_column is not None:
            _query = _query.order_by(order_column.asc())

        page = max(int(page), 1)
        per_page = int(limit if limit is not None else 10)
        pagination = _query.paginate(page=page, per_page=per_page, error_out=False)

        data = []
        for vehycle in pagination.items:
            data.append(vehycle.to_dict())

        return json_response(
            response = "OK",
            status_code = 200,
            data = data,
            total = pagination.total,
            page = pagination.page,
            pages = pagination.pages
        )

    except Exception as e:
        print("Error creating user:", e)
        print(traceback.format_exc())
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)

@vehycles_bp.route("ui", methods=["POST"])
#@firebase_auth_required
def upinsert_vehycle():
    try:
        from .models.vehycle_models import Vehycles
        data = request.get_json()
        print("Received data for upsert:", data)

        _vehycle = Vehycles.from_json(data)

        if (_vehycle.organization_uid_fk is None or _vehycle.organization_uid_fk == "") or (_vehycle.type is None or _vehycle.type == ""):
            print("Missing required fields: organization_uid_fk or type")
            return json_response(
                response="MISSING_FIELDS",
                status_code=400,
                data=[]
            )

        _selected = Vehycles.query.filter_by(uid=_vehycle.uid, organization_uid_fk=_vehycle.organization_uid_fk).first() if _vehycle.uid else None

        if _selected:
            for key, value in data.items():
                setattr(_selected, key, value)
            db.session.add(_selected)
            message = "UPDATED_SUCCESSFULLY"
            persisted = _selected
        else:
            _vehycle.uid = str(uuid.uuid4())
            db.session.add(_vehycle)
            message = "CREATED_SUCCESSFULLY"
            persisted = _vehycle

        db.session.commit()

        return json_response(
            response=message,
            status_code=201,
            data={"vehycle": persisted.to_dict()}
        )

    except Exception as e:
        print("Error creating/updating vehycle:", e)
        print(traceback.format_exc())
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)