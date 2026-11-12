from backend.apps.commerciall_api.main import db
from datetime import datetime, timezone

from backend.modules.person.services.address_services import address_upsert_service
from backend.modules.person.services.mail_services import mail_upsert, mail_upsert_service
from backend.modules.person.services.person_financial_services import financial_upsert_service
from backend.modules.person.services.person_legal_activity_services import activity_upsert_service
from backend.modules.person.services.person_legal_br_tax_regime_services import br_tax_regime_upsert_service
from backend.modules.person.services.person_legal_partner_services import partner_upsert_service
from backend.modules.person.services.person_legal_services import legal_upsert_service
from backend.modules.person.services.person_natural_services import natural_upsert_service
from backend.modules.person.services.person_supplementary_services import supplementary_upsert_service
from backend.modules.person.services.phone_services import phone_upsert_service
from backend.modules.utils.api_response import ApiResponse
from flask import current_app, request
from sqlalchemy import and_, or_

from backend.modules.utils.api_response import json_response
from ..models.person_model import Person
from sqlalchemy.orm import joinedload, selectinload

def person_list(data=None):
    current_app.logger.debug("person_list received data: %s", data)
    
    try:
        uid = int(data.get("u")) if data.get("u") else None
        person_type = int(data.get("pt")) if data.get("pt") else None
        name = data.get("n")
        id_number = data.get("in")
        name_or_id_number = data.get("noin") # search by name or id number
        is_supplier = data.get("is") # suppliers 
        person_type = int(data.get("pt")) if data.get("pt") else None
        main_organization_uid = int(data.get("mou")) if data.get("mou") else None
        only_active_fields = data.get("oaf") # only return active mails, phones and addresses
        only_users = data.get("ou") # inner join with users table (return only persons that are also users)
        only_drivers = data.get("od") # inner join with drivers table (return only persons that are also drivers)
        all_data = True if data.get("ad") == "1" else False # return all related data (mails, phones, addresses, person_natural/legal)
        page = int(data.get("p", 1))  # default to page 1
        page_limit = data.get("pl")  # limit of items per page
        order_by = data.get("ob")  # field to order by

        if (main_organization_uid in (None, 0, "") or person_type in (None, 0, "") or person_type not in (1, 2)):
            return json_response(response="MISSING_FIELDS")

        person_query = Person.query

        # Apply filters
        if uid is not None:
            person_query = person_query.filter(Person.uid == uid) 
        if name is not None:
            name_parts = name.split()
            syntax = and_(*[Person.name.ilike(f"%{part}%") for part in name_parts])
            person_query = person_query.filter(syntax)
        if id_number is not None:
            person_query = person_query.filter(Person.id_number.ilike(f"%{id_number}%"))
        if name_or_id_number is not None:
            #split the name by spaces and search each part
            name_parts = name_or_id_number.split()
            syntax = and_(*[Person.name.ilike(f"%{part}%") for part in name_parts])
            person_query = person_query.filter(or_(syntax, Person.id_number.ilike(f"%{name_or_id_number}%")))
        if only_active_fields in (2, "2", True, "true"):
            person_query = person_query.filter(Person.is_active == 2)  # only active persons
        if is_supplier is not None:
            is_supplier_bool = True if is_supplier.lower() == "true" else False
            person_query = person_query.filter(Person.is_supplier == is_supplier_bool)
        if person_type is not None:
            person_query = person_query.filter(Person.person_type == int(person_type))

        person_query = person_query.filter(Person.main_organization_uid_fk == main_organization_uid)

        if all_data:
            if person_type == 1: # natural
                person_query = person_query.options(selectinload(Person.natural))
            elif person_type == 2: # legal
                person_query = person_query.options(selectinload(Person.legal))
                person_query = person_query.options(selectinload(Person.activities if not only_active_fields else Person.activities.and_(Person.person_type == 2)))
                person_query = person_query.options(selectinload(Person.br_tax_regimes if not only_active_fields else Person.br_tax_regimes.and_(Person.person_type == 2)))
                person_query = person_query.options(selectinload(Person.partners if not only_active_fields else Person.partners.and_(Person.person_type == 2)))
            
            person_query = person_query.options(selectinload(Person.mails if not only_active_fields else Person.mails.and_(Person.mails.is_active == 1)))
            person_query = person_query.options(selectinload(Person.phones if not only_active_fields else Person.phones.and_(Person.phones.is_active == 1)))
            person_query = person_query.options(selectinload(Person.addresses if not only_active_fields else Person.addresses.and_(Person.addresses.is_active == 1)))
            person_query = person_query.options(selectinload(Person.accounts if not only_active_fields else Person.accounts.and_(Person.accounts.is_active == 1)))
            person_query = person_query.options(selectinload(Person.financial))
            person_query = person_query.options(selectinload(Person.supplementary))
            # only load legal partners for legal persons

        if only_users is not None and (only_users == "1"):
            person_query = person_query.join(Person.user_organizations).options(joinedload(Person.user_organizations)).distinct()
            
        if only_drivers is not None and (only_drivers == "1"):
            person_query = person_query.join(Person.vehycle_drivers).options(joinedload(Person.vehycle_drivers)).distinct()

        order_column = getattr(Person, order_by, None) if order_by is not None else None
        person_query = person_query.order_by(order_column.asc() if order_column is not None else Person.name.asc())

        page = max(int(request.args.get("page", 1)), 1)
        per_page = int(request.args.get("per_page", page_limit if page_limit is not None else 15))
        pagination = person_query.paginate(page=page, per_page=per_page, error_out=False)

        print(f"Pagination: {pagination.items}, Total: {pagination.total}, Page: {pagination.page}, Pages: {pagination.pages}")

        # Serialize data
        data = []
        for person in pagination.items:
            person_data = {}
            person_data["person"] = person.to_dict()
           
            data.append(person_data)

        print(f"Person data: {data}")
            
        return json_response(
            response = ApiResponse.REQUEST_SUCCESSFUL,
            data = data,
            total = pagination.total,
            page = pagination.page,
            pages = pagination.pages
        )

    except Exception:
        # Let the application's centralized Flask error handler format the response.
        raise


def person_upsert(data=None):
    current_app.logger.debug("person_upsert received data: %s", data)
    
    try:
        data = request.get_json()
        current_app.logger.debug("Received person natural data:", data)

        person_data = Person.from_json(data)
        
        if (person_data.main_organization_uid_fk in ("", None , 0)
                or person_data.name in ("", None) 
                or person_data.id_number in ("", None) 
                or person_data.person_type in ("", None)):
            
            return json_response(
                response="MISSING_FIELDS"
            )

        if person_data.uid in ("", None):
            duplicated = Person.query.filter(
                Person.main_organization_uid_fk == person_data.main_organization_uid_fk,
                Person.id_number == person_data.id_number
            ).first()
            if duplicated:
                return json_response(
                    response="ALREADY_EXISTS",
                )

        _selected = db.session.get(Person, person_data.uid)
        
        # Update existing record
        if _selected:
            print(f"Updating existing person with UID: {_selected.uid}")
            _selected.name = person_data.name
            _selected.id_number = person_data.id_number
            _selected.is_active = person_data.is_active
            _selected.is_supplier = person_data.is_supplier
            _selected.iso2alpha = person_data.iso2alpha
            _selected.created_at =_selected.created_at
            _selected.updated_at = datetime.now(timezone.utc)
            _selected.sync_status = "PENDING"
            message = ApiResponse.UPDATED_SUCCESSFULLY
            persisted_person =_selected

        # Create new record
        else:
            print("Creating new person record with UID: {selected.uid}")
            from uuid import uuid4 as Uuid4
            person_data.uid = Uuid4()
            person_data.created_at = datetime.now(timezone.utc)
            person_data.updated_at = datetime.now(timezone.utc)
            person_data.sync_status = "PENDING"
            message = ApiResponse.CREATED_SUCCESSFULLY
            persisted_person = person_data

        mails_list = data.get("mails", [])
        if mails_list:
            for mail in mails_list:
                mail_upsert_service(data=mail, person_uid_fk=persisted_person.uid, apply_commit=False)
        
        phones_list = data.get("phones", [])
        if phones_list:
            for phone in phones_list:
                phone_upsert_service(data=phone, person_uid_fk=persisted_person.uid, apply_commit=False)

        addresses_list = data.get("addresses", [])
        if addresses_list:
            for address in addresses_list:
                address_upsert_service(data=address, person_uid_fk=persisted_person.uid, apply_commit=False)

        br_tax_regimes_list = data.get("br_tax_regimes", [])
        if br_tax_regimes_list:
            for item in br_tax_regimes_list:
                br_tax_regime_upsert_service(data=item, person_uid_fk=persisted_person.uid, apply_commit=False)  

        activities_list = data.get("activities", [])
        if activities_list:
            for item in activities_list:
                activity_upsert_service(data=item, person_uid_fk=persisted_person.uid, apply_commit=False)

        partners_list = data.get("partners", [])
        if partners_list:
            for item in partners_list:
                partner_upsert_service(data=item, person_uid_fk=persisted_person.uid, apply_commit=False)

        financial = data.get("financial")
        if financial:
            financial_upsert_service(data=financial, person_uid_fk=persisted_person.uid, apply_commit=False)

        natural = data.get("natural")
        if natural:
            natural_upsert_service(data=natural, person_uid_fk=persisted_person.uid, apply_commit=False)

        supplementary = data.get("supplementary")
        if supplementary:
            supplementary_upsert_service(data=supplementary, person_uid_fk=persisted_person.uid, apply_commit=False)

        legal = data.get("legal")
        if legal:
            legal_upsert_service(data=legal, person_uid_fk=persisted_person.uid, apply_commit=False)
        
        db.session.commit()  
        print(f"Persisted person: {persisted_person.to_dict()}")
        return json_response(
            response=message,
            data=[persisted_person.to_dict()]
        )

    except Exception:
        # Let the application's centralized Flask error handler format the response.
        raise
