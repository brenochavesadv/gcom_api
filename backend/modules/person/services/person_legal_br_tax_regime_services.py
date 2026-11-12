
from backend.apps.commerciall_api.main import db
from datetime import datetime, timezone
from backend.modules.utils.api_response import ApiResponse
from flask import current_app
from backend.modules.utils.api_response import json_response, ApiResponse
from ..models.person_legal_br_tax_regime_model import PersonLegalBrTaxRegime
import traceback
import uuid

# upisert person legal br tax regime function to create or update a record
def br_tax_regime_upsert_service(data=None, person_uid_fk=None, apply_commit=True): 

    try:
        current_app.logger.debug("Received person legal br tax regime data: %s", data)

        _data = PersonLegalBrTaxRegime.from_json(data)

        if (_data.person_uid_fk in (None,"")) and person_uid_fk is not None:
            _data.person_uid_fk = person_uid_fk
        
        if (_data.person_uid_fk is None or _data.person_uid_fk == "") or (_data.tax_regime is None or _data.tax_regime == ""):
            current_app.logger.debug("Missing required fields: person_uid_fk or tax_regime")

            if apply_commit:
                return json_response(
                    response=ApiResponse.MISSING_FIELDS,
                )
            else:
                return

        _selected = db.session.get(PersonLegalBrTaxRegime, _data.uid)
        
        if _selected:
            _selected.tax_regime = _data.tax_regime
            _selected.year = _data.year
            _selected.scp_cnpj = _data.scp_cnpj
            _selected.accounting_records = _data.accounting_records
            _selected.created_at = _selected.created_at
            _selected.updated_at = datetime.now(timezone.utc)
            _selected.sync_status = "PENDING"

            response = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
        else:
            _data.uid = str(uuid.uuid4())
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
            data={"person_legal_br_tax_regime": persisted.to_dict()}
        )

    except Exception as e:
        raise
    
