
from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_

from api_app.constants.response import json_response
from ..models.person_model import Person
from ..models.person_legal_model import PersonLegal
from ..models.person_natural_model import PersonNatural
from ..docs.person import person_docs
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from sqlalchemy.orm import joinedload, selectinload
import traceback

person_bp = Blueprint("person", __name__)

def get_person(all_data=False, data=None):
    
    try:
        uid = data.get("u") if data.get("u") else None
        name = data.get("n")
        id_number = data.get("i")
        name_or_id_number = data.get("ni") # search by name or id number
        active = data.get("a") # only active persons
        supplier = data.get("s")
        person_type = int(data.get("t")) if data.get("t") else None
        organization = data.get("o")
        only_users = data.get("ou") # inner join with users table (return only persons that are also users)
        limit = data.get("limit")  # limit of items per page
        order_by = data.get("order")  # field to order by
        oaf = data.get("oaf") if data.get("oaf") is not None else False  # only active fields (mails, phones, addresses)

        if organization is None:
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

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
        if active is not None:
            is_active_bool = True if active.lower() == "true" else False
            person_query = person_query.filter(Person.is_active == is_active_bool)
        if supplier is not None:
            is_supplier_bool = True if supplier.lower() == "true" else False
            person_query = person_query.filter(Person.is_supplier == is_supplier_bool)
        if person_type is not None:
            person_query = person_query.filter(Person.person_type == int(person_type))

        person_query = person_query.filter(Person.main_organization_uid_fk == organization)

        if all_data:
            if person_type == 1: # natural
                person_query = person_query.options(selectinload(Person.person_natural))
            elif person_type == 2: # legal
                person_query = person_query.options(selectinload(Person.person_legal))
            
            person_query = person_query.options(selectinload(Person.mail if not oaf else Person.mail.and_(Person.mail.is_active == 1)))
            person_query = person_query.options(selectinload(Person.phone if not oaf else Person.phone.and_(Person.phone.is_active == 1)))
            person_query = person_query.options(selectinload(Person.address if not oaf else Person.address.and_(Person.address.is_active == 1)))

        if only_users is not None and (only_users == "1"):
            person_query = person_query.join(Person.user_organizations).options(joinedload(Person.user_organizations)).distinct()
            
        order_column = getattr(Person, order_by, None) if order_by is not None else None
        person_query = person_query.order_by(order_column.asc() if order_column is not None else Person.name.asc())

        page = max(int(request.args.get("page", 1)), 1)
        per_page = int(request.args.get("per_page", limit if limit is not None else 15))
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
                        person_data["family"] = person.person_natural.family_to_dict()
                        person_data["profession"] = person.person_natural.profession_to_dict()
                elif person_type==2:
                    if person.person_legal:
                        person_data["person_legal"] = person.person_legal.to_dict()
            
                # Add related data
                if person.phone:
                    phones = person.phone if not oaf else [p for p in person.phone if p.is_active == 1]
                    person_data["phones"] = [phone.to_dict() for phone in phones]
                if person.mail:
                    mails = person.mail if not oaf else [m for m in person.mail if m.is_active == 1]
                    person_data["mails"] = [mail.to_dict() for mail in mails]
                if person.address:
                    addresses = person.address if not oaf else [a for a in person.address if a.is_active == 1]
                    person_data["addresses"] = [address.to_dict() for address in addresses]
           
            data.append(person_data)

        return json_response(
            response = "OK",
            status_code = 200,
            data = data,
            total = pagination.total,
            page = pagination.page,
            pages = pagination.pages
        )

    except Exception as e:
        print(f"get_person error: {str(e)}")
        print(traceback.format_exc())
        return json_response(response="INTERNAL_ERROR", status_code=500)

@person_bp.route("/list", methods=["POST"])
#@firebase_auth_required
@swag_from(person_docs["list_person"])
def list_person():
    data = request.get_json()
    return get_person(all_data=False, data=data)