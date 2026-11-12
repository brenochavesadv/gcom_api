
from backend.apps.commerciall_api.main import db
from backend.modules.utils.get_date_on_utc import getDateOnUTC
from ..models.person_natural_model import PersonNatural

def natural_upsert_service(data: None, person_uid_fk=None, apply_commit: bool = True):
    try:

        _data = PersonNatural.from_json(data)

        _selected = db.session.get(PersonNatural, person_uid_fk)
        
        if _selected:
            _selected.id_card = _data.id_card
            _selected.id_issuer = _data.id_issuer
            _selected.birth_date = _data.birth_date
            _selected.birth_city = _data.birth_city
            _selected.pronoun = _data.pronoun
            _selected.nickname = _data.nickname
            _selected.gender = _data.gender
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
