
from backend.apps.commerciall_api.main import db
from datetime import datetime, timezone
from backend.modules.utils.api_response import ApiResponse
from flask import current_app
from backend.modules.utils.api_response import json_response, ApiResponse
from ..models.address_model import Address
import traceback

# upisert_address function to create or update an address record
def address_upsert_service(data=None, person_uid_fk=None, apply_commit=True): 

    try:
        _data = Address.from_json(data) 
        
        current_app.logger.debug("upsert_address person_uid_fk: %s, data: %s", person_uid_fk, data)
        address_data = Address.from_json(data)

        if (_data.person_uid_fk  in (None,"")) and person_uid_fk is not None:
            _data.person_uid_fk = person_uid_fk

        if (_data.person_uid_fk in (None,"")) or (_data.address in (None,"")):
            current_app.logger.debug("Missing required fields: person_uid_fk or address")
            if apply_commit:
                return json_response(
                    response=ApiResponse.MISSING_FIELDS,
                )
            else:
                return None

        if _data.is_main == 1:
            # Set all other addresses for this person to not main
            Address.query.filter(Address.person_uid_fk == _data.person_uid_fk, Address.uid != _data.uid).update({"is_main": 0})
            
        _selected = db.session.get(Address, _data.uid)

        if _selected:
            _selected.address = _data.address
            _selected.address_label = _data.address_label
            _selected.suffix = _data.suffix
            _selected.number = _data.number
            _selected.complement = _data.complement
            _selected.nbhd = _data.nbhd
            _selected.zip_code = _data.zip_code
            _selected.city_code = _data.city_code
            _selected.city_name = _data.city_name
            _selected.state_abbrev = _data.state_abbrev
            _selected.state_name = _data.state_name
            _selected.iso2alpha = _data.iso2alpha
            _selected.is_active = _data.is_active
            _selected.is_main =_data.is_main  
            _selected.created_at = _selected.created_at
            _selected.updated_at = datetime.now(timezone.utc)
            _selected.sync_status = "PENDING"
            
            response = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
            
        else:
            #from uuid import uuid4 as Uuid4
            #_data.uid = Uuid4() // db uses integer auto increment for primary key, so no need to set uid manually
            _data.created_at = datetime.now(timezone.utc)
            _data.updated_at = datetime.now(timezone.utc)
            _data.sync_status = "PENDING"
            db.session.add(_data)
            response = ApiResponse.CREATED_SUCCESSFULLY
            persisted = _data

        if apply_commit:
            db.session.commit()

        return json_response(
            response=response,
            data={"address": persisted.to_dict()}
        )

    except Exception as e:
        raise
