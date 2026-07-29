from api_app.modules.utils.api_response import ApiResponse
from flask import current_app, request
from sqlalchemy import and_, or_

from api_app.modules.utils.api_response import json_response, ApiResponse
from ..models.person_model import Person
from sqlalchemy.orm import joinedload, selectinload
import traceback

def get_person(data=None):
    current_app.logger.debug("get_person data: %s", data)
    
    try:
        uid = int(data.get("u")) if data.get("u") else None
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

        if (main_organization_uid in (None, 0, "") or person_type in (None, 0, "")):
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
        if only_active_fields is not None:
            is_active_bool = True if only_active_fields.lower() == "true" else False
            person_query = person_query.filter(Person.is_active == is_active_bool)
        if is_supplier is not None:
            is_supplier_bool = True if is_supplier.lower() == "true" else False
            person_query = person_query.filter(Person.is_supplier == is_supplier_bool)
        if person_type is not None:
            person_query = person_query.filter(Person.person_type == int(person_type))

        person_query = person_query.filter(Person.main_organization_uid_fk == main_organization_uid)

        if all_data:
            if person_type == 1: # natural
                person_query = person_query.options(selectinload(Person.person_natural))
            elif person_type == 2: # legal
                person_query = person_query.options(selectinload(Person.person_legal))
            
            person_query = person_query.options(selectinload(Person.mail if not only_active_fields else Person.mail.and_(Person.mail.is_active == 1)))
            person_query = person_query.options(selectinload(Person.phone if not only_active_fields else Person.phone.and_(Person.phone.is_active == 1)))
            person_query = person_query.options(selectinload(Person.address if not only_active_fields else Person.address.and_(Person.address.is_active == 1)))
            person_query = person_query.options(selectinload(Person.person_legal_activity.and_(Person.person_type == 2))) # only load legal activities for legal persons
            person_query = person_query.options(selectinload(Person.person_legal_br_tax_regime.and_(Person.person_type == 2))) # only load legal tax regimes for legal persons
            person_query = person_query.options(selectinload(Person.person_legal_partner.and_(Person.person_type == 2))) # only load legal partners for legal persons

        if only_users is not None and (only_users == "1"):
            person_query = person_query.join(Person.user_organizations).options(joinedload(Person.user_organizations)).distinct()
            
        if only_drivers is not None and (only_drivers == "1"):
            person_query = person_query.join(Person.vehycle_drivers).options(joinedload(Person.vehycle_drivers)).distinct()

        order_column = getattr(Person, order_by, None) if order_by is not None else None
        person_query = person_query.order_by(order_column.asc() if order_column is not None else Person.name.asc())

        page = max(int(request.args.get("page", 1)), 1)
        per_page = int(request.args.get("per_page", page_limit if page_limit is not None else 15))
        pagination = person_query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize data
        data = []
        for person in pagination.items:
            person_data = {}
            person_data["person"] = person.to_dict()

            if all_data:
                if person_type==1:
                    if person.person_natural:
                        person_data["person_natural"] = person.person_natural.to_dict()
                elif person_type==2:
                    if person.person_legal:
                        person_data["person_legal"] = person.person_legal.to_dict()
            
                # Add related data
                if person.phone:
                    phones = person.phone if not only_active_fields else [p for p in person.phone if p.is_active == 1]
                    person_data["phones"] = [phone.to_dict() for phone in phones]
                if person.mail:
                    mails = person.mail if not only_active_fields else [m for m in person.mail if m.is_active == 1]
                    person_data["mails"] = [mail.to_dict() for mail in mails]
                if person.address:
                    addresses = person.address if not only_active_fields else [a for a in person.address if a.is_active == 1]
                    person_data["addresses"] = [address.to_dict() for address in addresses]

                if person.person_type == 2:  # person legal
                    if person.person_legal_activity:
                        person_data["person_legal_activities"] = [activity.to_dict() for activity in person.person_legal_activity]
                    if person.person_legal_br_tax_regime:
                        person_data["person_legal_br_tax_regimes"] = [tax_regime.to_dict() for tax_regime in person.person_legal_br_tax_regime]
                    if person.person_legal_partner:
                        person_data["person_legal_partners"] = [partner.to_dict() for partner in person.person_legal_partner]
           
            data.append(person_data)
            
        return json_response(
            response = ApiResponse.REQUEST_SUCCESSFUL,
            data = data,
            total = pagination.total,
            page = pagination.page,
            pages = pagination.pages
        )

    except Exception as e:
        current_app.logger.debug(f"get_person error: {str(e)}")
        current_app.logger.debug(traceback.format_exc())
        return json_response(response=ApiResponse.INTERNAL_ERROR)