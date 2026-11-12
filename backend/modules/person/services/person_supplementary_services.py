
from backend.apps.commerciall_api.main import db
from backend.modules.utils.get_date_on_utc import getDateOnUTC
from ..models.person_supplementary_model import PersonSupplementary

def supplementary_upsert_service(data:None, person_uid_fk=None, apply_commit: bool = True) -> PersonSupplementary:
    try:
        _data = PersonSupplementary.from_json(data)
        
        _selected = db.session.get(PersonSupplementary, person_uid_fk)
        
        if _selected:
            _selected.father_name=_data.father_name
            _selected.mother_name=_data.mother_name
            _selected.profession=_data.profession
            _selected.professional_id=_data.professional_id
            _selected.salary=_data.salary
            _selected.employer=_data.employer
            _selected.employer_contact=_data.employer_contact
            _selected.other_incomes=_data.other_incomes
            _selected.incomes_sum=_data.incomes_sum
            _selected.file_income_tax=_data.file_income_tax
            _selected.marital_status=_data.marital_status
            _selected.children=_data.children
            _selected.alimony=_data.alimony
            _selected.spouse=_data.spouse
            _selected.spouse_id_card=_data.spouse_id_card
            _selected.spouse_profession=_data.spouse_profession
            _selected.spouse_employer=_data.spouse_employer
            _selected.spouse_incomes=_data.spouse_incomes
            _selected.spouse_phone=_data.spouse_phone
            _selected.spouse_email=_data.spouse_email
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
