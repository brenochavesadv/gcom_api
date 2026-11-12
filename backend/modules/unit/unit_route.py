from datetime import datetime
from flask import Blueprint, current_app, request

from backend.modules.utils.api_response import ApiResponse, json_response
from ..auth_firebase.firebase_decorators import firebase_auth_required
from sqlalchemy.orm import joinedload, selectinload
from .unit_model import Unit

unit_bp = Blueprint("unit", __name__)

@unit_bp.route("/l", methods=["POST"])
@firebase_auth_required
#@swag_from(product_docs["list_product"])
def list_unit():
    try:
        data = request.get_json() or {}
        uid = data.get("u")
        is_active = data.get("ia")
        type = data.get("t")
        order_by = data.get("ob", "pt_br")  # Default order by pt_br
       
        query = Unit.query

        if uid not in (None, ""):
            query = query.filter(Unit.uid == uid)
        if is_active not in (None, ""):
            query = query.filter(Unit.is_active == is_active)
        if type not in (None, ""):
            if type == 2:
                query = query.filter(Unit.type != 3) # exclude 'service'
            elif type == 3:
                query = query.filter(Unit.type != 2)  # exclude 'product'
        if order_by not in (None, ""):
            query = query.order_by(getattr(Unit, order_by).asc())

        result = query.all()

        units = []
        for item in result:
            units.append(item.to_dict())

        #print(f"Unit data: {units}")  # Debugging line to print the query results

        return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = units
                )

    except Exception as e:
        import traceback
        current_app.logger.debug(f"Unit list error: {traceback.format_exc()}")
        raise
