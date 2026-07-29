
from main import db
from datetime import datetime
from api_app.modules.utils.api_response import ApiResponse
from flask import current_app
from api_app.modules.utils.api_response import json_response, ApiResponse
from ..models.person_legal_br_tax_regime_model import PersonLegalBrTaxRegime
import traceback
import uuid

# upisert person legal br tax regime function to create or update a record
def upinsert_pl_br_tax_regime(data=None, person_uid_fk=None, auto_commit=True): 

    try:
        current_app.logger.debug("Received person legal br tax regime data: %s", data)

        regime_data = PersonLegalBrTaxRegime.from_json(data)

        if (regime_data.person_uid_fk in (None,"")) and person_uid_fk is not None:
            regime_data.person_uid_fk = person_uid_fk
        
        if (regime_data.person_uid_fk is None or regime_data.person_uid_fk == "") or (regime_data.tax_regime is None or regime_data.tax_regime == ""):
            current_app.logger.debug("Missing required fields: person_uid_fk or tax_regime")

            if auto_commit:
                return json_response(
                    response=ApiResponse.MISSING_FIELDS,
                )
            else:
                return

        _selected = PersonLegalBrTaxRegime.query.filter_by(uid=regime_data.uid).first() if regime_data.uid else None
        if not _selected:
            _selected = PersonLegalBrTaxRegime.query.filter_by(person_uid_fk=regime_data.person_uid_fk, year=regime_data.year).first() if regime_data.person_uid_fk and regime_data.year else None

        if _selected:
            _selected.tax_regime = regime_data.tax_regime
            _selected.year = regime_data.year
            _selected.scp_cnpj = regime_data.scp_cnpj
            _selected.accounting_records = regime_data.accounting_records
            _selected.sync_status = regime_data.sync_status
            _selected.updated_at = datetime.now()

            response = ApiResponse.UPDATED_SUCCESSFULLY
            persisted = _selected
        else:
            regime_data.uid = str(uuid.uuid4())
            regime_data.created_at = datetime.now()
            regime_data.updated_at = datetime.now()
            db.session.add(regime_data)
            response = ApiResponse.CREATED_SUCCESSFULLY
            persisted = regime_data

        if auto_commit:
            db.session.commit()
        else:
            db.session.flush()

        return json_response(
            response=response,
            data={"person_legal_br_tax_regime": persisted.to_dict()}
        )

    except Exception as e:
        current_app.logger.debug("Error creating/updating person legal br tax regime: %s", e)
        current_app.logger.debug(traceback.format_exc())
        if auto_commit:
            db.session.rollback()
        else:
            db.session.flush()
            return

    return json_response(response=ApiResponse.INTERNAL_ERROR)
    