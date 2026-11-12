
from flask import current_app

from backend.apps.commerciall_api.main import db
from backend.modules.utils.api_response import ApiResponse, json_response
from backend.modules.utils.get_date_on_utc import getDateOnUTC
from ..models.person_financial_model import PersonFinancial



def financial_upsert_service(data: None, person_uid_fk=None, apply_commit: bool = True):
    try:

        _data = PersonFinancial.from_json(data)

        if person_uid_fk:
            _data.person_uid_fk = person_uid_fk

        _selected = db.session.get(PersonFinancial, _data.person_uid_fk)
        
        if _selected:
            _selected.credit_limit = _data.credit_limit
            _selected.credit_balance = _data.credit_balance
            _selected.is_credit_available = _data.is_credit_available
            _selected.block_exceeding_limit = _data.block_exceeding_limit
            _selected.updated_at = getDateOnUTC(None)
            _selected.sync_status = "PENDING"
            
        else:
            _data.person_uid_fk = person_uid_fk
            _data.created_at = getDateOnUTC(None)
            _data.updated_at = getDateOnUTC(None)
            _data.sync_status = "PENDING"
            db.session.add(_data)

        if apply_commit:
            db.session.commit()      

    except Exception as e:
        if apply_commit:
            db.session.rollback()
        raise
