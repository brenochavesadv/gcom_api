
from backend.apps.commerciall_api.main import db
from backend.modules.utils.get_date_on_utc import getDateOnUTC
from ..models.person_legal_model import PersonLegal



def legal_upsert_service(data: None, person_uid_fk=None, apply_commit: bool = True):
    try:

        _data = PersonLegal.from_json(data)

        _selected = db.session.get(PersonLegal, person_uid_fk)
        
        if _selected:
            _selected.commercial_name = _data.commercial_name
            _selected.person_legal_type = _data.person_legal_type
            _selected.share_capital = _data.share_capital
            _selected.revenue = _data.revenue
            _selected.person_legal_size = _data.person_legal_size
            _selected.register_status = _data.register_status
            _selected.register_status_reason = _data.register_status_reason
            _selected.register_status_date = _data.register_status_date
            _selected.special_situation = _data.special_situation
            _selected.special_situation_date = _data.special_situation_date
            _selected.is_headquarter = _data.is_headquarter
            _selected.is_simples_regime = _data.is_simples_regime
            _selected.simples_admission_date = _data.simples_admission_date
            _selected.simples_exclusion_date = _data.simples_exclusion_date
            _selected.is_mei_regime = _data.is_mei_regime
            _selected.mei_admission_date = _data.mei_admission_date
            _selected.mei_exclusion_date = _data.mei_exclusion_date
            _selected.contact_name = _data.contact_name
            _selected.foundation_date = _data.foundation_date
            _selected.tax_state_id = _data.tax_state_id
            _selected.tax_city_id = _data.tax_city_id
            _selected.responsible_entity = _data.responsible_entity
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
        raise
