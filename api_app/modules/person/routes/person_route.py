
from flask import Blueprint, request, jsonify

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

def get_person(all_data=False):
    
    try:
        uid = request.args.get("u") if request.args.get("u") else None
        name = request.args.get("n")
        active = request.args.get("a") # only active persons
        supplier = request.args.get("s")
        person_type = int(request.args.get("t")) if request.args.get("t") else None
        organization = request.args.get("o")
        id_number = request.args.get("i")
        limit = request.args.get("limit")  # limit of items per page
        order_by = request.args.get("order")  # field to order by
        oaf = request.args.get("oaf") if request.args.get("oaf") is not None else False  # only active fields (mails, phones, addresses)

        if organization is None:
            return jsonify({"error": "Organization is required"}), 400

        person_query =  Person.query.filter(Person.main_organization_uid_fk == organization)

        # Apply filters
        if uid is not None:
            person_query =  person_query.filter(Person.uid == uid)
        if name is not None:
            #split the name by spaces and search each part
            name_parts = name.split()
            for part in name_parts:
                person_query =  person_query.filter(Person.name.ilike(f"%{part}%"))
        if active is not None:
            is_active_bool = True if active.lower() == "true" else False
            person_query =  person_query.filter(Person.is_active == is_active_bool)
        if supplier is not None:
            is_supplier_bool = True if supplier.lower() == "true" else False
            person_query =  person_query.filter(Person.is_supplier == is_supplier_bool)
        if person_type is not None:
            person_query =  person_query.filter(Person.person_type == int(person_type))
        if id_number is not None:
            person_query =  person_query.filter(Person.id_number == id_number)

        if all_data:
            if person_type == 1: # natural
                person_query = person_query.options(selectinload(Person.person_natural))
            elif person_type == 2: # legal
                person_query = person_query.options(selectinload(Person.person_legal))
            
            person_query = person_query.options(selectinload(Person.mail if not oaf else Person.mail.and_(Person.mail.is_active == 1)))
            person_query = person_query.options(selectinload(Person.phone if not oaf else Person.phone.and_(Person.phone.is_active == 1)))
            person_query = person_query.options(selectinload(Person.address if not oaf else Person.address.and_(Person.address.is_active == 1)))

        person_query =  person_query.order_by(getattr(Person, order_by).asc() if order_by is not None else Person.name.asc())

        page = int(request.args.get("page", 1))
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

@person_bp.route("/list", methods=["GET"])
#@firebase_auth_required
@swag_from(person_docs["list_person"])
def list_person():
    return get_person(all_data=False)