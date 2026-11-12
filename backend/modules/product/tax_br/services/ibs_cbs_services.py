from datetime import datetime, timezone
import traceback
from uuid import uuid4

from flask import current_app

from backend.apps.commerciall_api.main import db
from backend.modules.utils.api_response import ApiResponse, json_response

from ..models.ibs_cbs_model import IbsCbs

def ibs_cbs_list_service(uid, organization_uid_fk):
    try:

        if organization_uid_fk in (None, ""):
            return json_response(response="MISSING_FIELDS")

        query = IbsCbs.query.filter(IbsCbs.organization_uid_fk == organization_uid_fk)

        if uid not in (None, ""):
            query = query.filter(IbsCbs.uid == uid)

        query = query.order_by(IbsCbs.description.asc()).all()  # Order by name ascending

        data = []
        for item in query:
            data.append(item.to_dict())

        return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = data,
        )

    except Exception as e:
        import traceback
        current_app.logger.debug(f"Ibs Cbs list error: {traceback.format_exc()}")
        raise

def ibs_cbs_upsert_service(data):
    
    try:
        print (f"Received data for upsert Ibs Cbs: {data}")  # Debugging line to print the received data

        item = IbsCbs.from_json(data["ibs_cbs"])

        if (item.organization_uid_fk in (None, "") or item.description in (None, "")):
            current_app.logger.debug("Missing required fields: uid, organization_uid_fk, or description")
            return json_response(
                response=ApiResponse.MISSING_FIELDS
            )

        _selected = IbsCbs.query.filter_by(uid=item.uid, organization_uid_fk=item.organization_uid_fk).first()
        persisted = None

        if _selected:
            # Update 
            _selected.description = item.description
            _selected.updated_at = datetime.now(timezone.utc)
            _selected.sync_status = "PENDING"
            
            message = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
            
        else:
            # Create 

            item.uid = str(uuid4())
            item.sync_status = "PENDING"
            item.updated_at = datetime.now(timezone.utc)
            item.created_at = datetime.now(timezone.utc)
            db.session.add(item)

            message = ApiResponse.CREATED_SUCCESSFULLY
            persisted = item

        db.session.commit()

        return json_response(
            response=message,
            data={"group": persisted.to_dict()}
        )

    except Exception as e:
        current_app.logger.debug(
            "Error upserting Ibs Cbs description: %s", e
        )
        current_app.logger.debug(traceback.format_exc())
        db.session.rollback()
        raise

