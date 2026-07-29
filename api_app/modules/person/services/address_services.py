
from main import db
from datetime import datetime
from api_app.modules.utils.api_response import ApiResponse
from flask import current_app
from api_app.modules.utils.api_response import json_response, ApiResponse
from ..models.address_model import Address
import traceback

# upisert_address function to create or update an address record
def upinsert_address(data=None, person_uid_fk=None, auto_commit=True): 

    try:
        current_app.logger.debug("upinsert_address person_uid_fk: %s, data: %s", person_uid_fk, data)
        address_data = Address.from_json(data)

        if (address_data.person_uid_fk  in (None,"")) and person_uid_fk is not None:
            address_data.person_uid_fk = person_uid_fk

        if (address_data.person_uid_fk in (None,"")) or (address_data.address in (None,"")):
            current_app.logger.debug("Missing required fields: person_uid_fk or address")
            if auto_commit:
                return json_response(
                    response=ApiResponse.MISSING_FIELDS,
                )
            else:
                return None

        if address_data.is_main == 1:
            # Set all other addresses for this person to not main
            Address.query.filter(Address.person_uid_fk == address_data.person_uid_fk, Address.uid != address_data.uid).update({"is_main": 0})
            
        _selected = Address.query.filter_by(uid=address_data.uid).first() if address_data.uid else None
        if not _selected:
            _selected = Address.query.filter_by(person_uid_fk=address_data.person_uid_fk, address=address_data.address, number=address_data.number, 
                                                complement=address_data.complement).first() if address_data.person_uid_fk and address_data.address else None

        if _selected:
            _selected.address = address_data.address
            _selected.address_label = address_data.address_label
            _selected.suffix = address_data.suffix
            _selected.number = address_data.number
            _selected.complement = address_data.complement
            _selected.nbhd = address_data.nbhd
            _selected.zip_code = address_data.zip_code
            _selected.city_code = address_data.city_code
            _selected.city_name = address_data.city_name
            _selected.state_abbrev = address_data.state_abbrev
            _selected.state_name = address_data.state_name
            _selected.iso2alpha = address_data.iso2alpha
            _selected.is_active = address_data.is_active
            _selected.is_main =address_data.is_main  
            _selected.updated_at = datetime.now()
            
            response = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
            
        else:
            address_data.created_at = datetime.now()
            address_data.updated_at = datetime.now()
            db.session.add(address_data)
            response = ApiResponse.CREATED_SUCCESSFULLY
            persisted = address_data

        if auto_commit:
            db.session.commit()
        else:
            db.session.flush()

        return json_response(
            response=response,
            data={"address": persisted.to_dict()}
        )

    except Exception as e:
        current_app.logger.debug("Error creating/updating address: %s", e)
        current_app.logger.debug(traceback.format_exc())
        if auto_commit:
            db.session.rollback()
        else:
            db.session.flush()
            return None
    
    return json_response(response=ApiResponse.INTERNAL_ERROR, exception=str(e))