import traceback
import uuid
from backend.apps.commerciall_api.main import db

from datetime import datetime, timezone
from flask import current_app
from backend.modules.utils.api_response import ApiResponse, json_response
from ..models.icms_pis_cofins_group_model import IcmsPisCofinsGroup
from ..models.icms_pis_cofins_item_model import IcmsPisCofinsItem
from ..models.cfop_model import Cfop
from sqlalchemy.orm import selectinload

def cfop_list_service(data=None):
    """Return the CFOP catalog used by the ICMS/PIS/COFINS editor."""
    try:
        query = Cfop.query.order_by(Cfop.cfop.asc()).all()
        return json_response(
            response=ApiResponse.REQUEST_SUCCESSFUL,
            data=[item.to_dict() for item in query],
        )
    except Exception:
        current_app.logger.debug("CFOP list error: %s", traceback.format_exc())
        raise

def icms_pis_cofins_list_service(uid, organization_uid_fk):
    try:

        if organization_uid_fk in (None, ""):
            return json_response(response="MISSING_FIELDS")

        query = IcmsPisCofinsGroup.query.filter(IcmsPisCofinsGroup.organization_uid_fk == organization_uid_fk)

        if uid not in (None, ""):
            query = query.filter(IcmsPisCofinsGroup.uid == uid).options(selectinload(IcmsPisCofinsGroup.items))

        query = query.order_by(IcmsPisCofinsGroup.description.asc()).all()  # Order by name ascending

        data = []
        for item in query:
            data.append(item.to_dict())

        return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = data,
        )

    except Exception as e:
        import traceback
        current_app.logger.debug(f"Icms Pis Cofins list error: {traceback.format_exc()}")
        raise

def upsert_icms_pis_cofins_description_service(data):
    
    try:
        print (f"Received data for upsert Icms Pis Cofins: {data}")  # Debugging line to print the received data

        uid = data.get("uid")
        organization_uid_fk = data.get("ou")
        description = data.get("description")

        if (organization_uid_fk in (None, "") or description in (None, "")):
            current_app.logger.debug("Missing required fields: uid, main_organization_uid_fk, or description")
            return json_response(
                response=ApiResponse.MISSING_FIELDS
            )

        _selected = IcmsPisCofinsGroup.query.filter_by(uid=uid, organization_uid_fk=organization_uid_fk).first()
        persisted = None

        if _selected:
            # Update description of existing group
            _selected.description = description
            _selected.updated_at = datetime.now(timezone.utc)
            _selected.sync_status = "PENDING"
            
            message = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
            
        else:
            # Create new group with default CFOP items

            default_cfops = {
                    "cfop_sell_same_uf": { "uid": str(uuid.uuid4()), "cfop": 5102 },
                    "cfop_sell_other_uf": { "uid": str(uuid.uuid4()), "cfop": 6102 },
                    "cfop_sell_export": { "uid": str(uuid.uuid4()), "cfop": 7102 },
                    "cfop_buy_same_uf": { "uid": str(uuid.uuid4()), "cfop": 1102 },
                    "cfop_buy_other_uf": { "uid": str(uuid.uuid4()), "cfop": 2102 },
                    "cfop_buy_import": { "uid": str(uuid.uuid4()), "cfop": 3102 }
                }

            # add default Icms Pis Cofins items for the new group

            group_uid = str(uuid.uuid4())
                        
            for item in default_cfops.items():
                _item = IcmsPisCofinsItem()
                _item.uid = item[1]["uid"]
                _item.icms_pis_cofins_group_uid_fk = group_uid
                _item.cfop = item[1]["cfop"]
                _item.updated_at = datetime.now(timezone.utc)
                _item.created_at = datetime.now(timezone.utc)
                db.session.add(_item)

            # The group is added below in the same transaction.  Do not flush
            # the child items before their parent exists.
            # add new Icms Pis Confins group
            
            _data = IcmsPisCofinsGroup()
            _data.uid = group_uid
            _data.organization_uid_fk = organization_uid_fk
            _data.description = description
            _data.cfop_sell_same_uf_item_uid_fk = default_cfops["cfop_sell_same_uf"]["uid"]
            _data.cfop_sell_other_uf_item_uid_fk = default_cfops["cfop_sell_other_uf"]["uid"]
            _data.cfop_sell_export_item_uid_fk = default_cfops["cfop_sell_export"]["uid"]
            _data.cfop_buy_same_uf_item_uid_fk = default_cfops["cfop_buy_same_uf"]["uid"]
            _data.cfop_buy_other_uf_item_uid_fk = default_cfops["cfop_buy_other_uf"]["uid"]
            _data.cfop_buy_import_item_uid_fk = default_cfops["cfop_buy_import"]["uid"]
            _data.updated_at = datetime.now(timezone.utc)
            _data.created_at = datetime.now(timezone.utc)
            db.session.add(_data)

            message = ApiResponse.CREATED_SUCCESSFULLY
            persisted = _data

        db.session.commit()

        return json_response(
            response=message,
            data={"group": persisted.to_dict()}
        )

    except Exception as e:
        current_app.logger.debug(
            "Error upserting Icms Pis Cofins description: %s", e
        )
        current_app.logger.debug(traceback.format_exc())
        db.session.rollback()
        raise

    
def update_icms_pis_cofins_item_service(data):

    try:
        print (f"Received data for upsert Icms Pis Cofins Item: {data}")  # Debugging line to print the received data

        _item = IcmsPisCofinsItem.from_json(data['icmsPisCofinsItem'])

        if (_item.uid in (None, "")):
            current_app.logger.debug("Missing required field uid for upsert Icms Pis Cofins Item")
            return json_response(
                response=ApiResponse.MISSING_FIELDS
            )

        group_uid = data['icmsPisCofinsItem'].get('icms_pis_cofins_group_uid_fk')
        if group_uid in (None, ""):
            return json_response(response=ApiResponse.MISSING_FIELDS)
        group = None
        if group_uid:
            group = IcmsPisCofinsGroup.query.filter_by(uid=group_uid).first()
            if group is None:
                return json_response(response=ApiResponse.NOT_FOUND)

        _selected_item = IcmsPisCofinsItem.query.filter_by(uid=_item.uid).first()

        if _selected_item:
            IcmsPisCofinsItem.updatable_fields(_selected_item, _item)
            _selected_item.updated_at = datetime.now(timezone.utc)
            _selected_item.sync_status = "PENDING"

            message = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected_item

            cfop_type = data.get('cfopType')
            if group is not None and cfop_type:
                setattr(group, f'{cfop_type}_item_uid_fk', _selected_item.uid)

            db.session.commit()

            return json_response(
                        response=message,
                        data={"icms_pis_cofins_item": persisted.to_dict()}
                    )
            
        else:
            current_app.logger.debug("Register not found for upsert Icms Pis Cofins Item with uid: %s", _item.uid)
            if _item.uid != "0":
                return json_response(response=ApiResponse.NOT_FOUND)
            db.session.add(_item)
            persisted = _item
            message = ApiResponse.CREATED_SUCCESSFULLY
            db.session.commit()
            return json_response(
                response=message,
                data={"icms_pis_cofins_item": persisted.to_dict()},
            )

        
        

        

    except Exception as e:
        current_app.logger.debug(
            "Error creating/updating icms_pis_cofins_item: %s", e
        )
        current_app.logger.debug(traceback.format_exc())
        db.session.rollback()
        raise


# Compatibility name used by the tax configuration routes and older clients.
upsert_icms_pis_cofins_item_service = update_icms_pis_cofins_item_service


def icms_pis_cofins_get_items_service(uid):
    """Return one ICMS/PIS/COFINS group with its configured items."""
    try:
        group = IcmsPisCofinsGroup.query.filter_by(uid=uid).first()
        if group is None:
            return json_response(
                response=ApiResponse.NO_DATA,
                data={"error": "Icms Pis Cofins group not found"},
            )
        return json_response(response=ApiResponse.REQUEST_SUCCESSFUL, data=group.to_dict())
    except Exception:
        current_app.logger.debug("Icms Pis Cofins items error: %s", traceback.format_exc())
        raise
