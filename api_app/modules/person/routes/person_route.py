from datetime import datetime
from shlex import join
from flask import Blueprint, request, jsonify
from ..models.person_model import Person
from ..models.person_legal_model import PersonLegal
from ..models.person_natural_model import PersonNatural
from ..models.phone_model import Phone
from ..models.mail_model import Mail
from ..models.address_model import Address
from ..docs.person import person_docs
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from sqlalchemy.orm import joinedload

person_bp = Blueprint("person", __name__)

def get_person(all_data=False):
    try:
        uid = int(request.args.get("u")) if request.args.get("u") else None
        name = request.args.get("n")
        active = request.args.get("a") # only active persons
        supplier = request.args.get("s")
        type = int(request.args.get("t")) if request.args.get("t") else None
        organization = request.args.get("o")
        limit = request.args.get("limit")  # limit of items per page
        order_by = request.args.get("order")  # field to order by
        oaf = request.args.get("oaf") if request.args.get("oaf") is not None else False  # only active fields (mails, phones, addresses)

        if organization is None:
            return jsonify({"error": "Organization is required"}), 400
                
        query = Person.query.filter(Person.organization_uid_fk == organization)
        
        # Apply filters
        if uid is not None:
            query = query.filter(Person.person_uid == uid)
        if name is not None:
            #split the name by spaces and search each part
            name_parts = name.split()
            for part in name_parts:
                query = query.filter(Person.name.ilike(f"%{part}%"))
        if active is not None:
            is_active_bool = True if active.lower() == "true" else False
            query = query.filter(Person.is_active == is_active_bool)
        if supplier is not None:
            is_supplier_bool = True if supplier.lower() == "true" else False
            query = query.filter(Person.is_supplier == is_supplier_bool)
        if type is not None:
            query = query.filter(Person.person_type == int(type))
        if id_number is not None:
            query = query.filter(Person.id_number == id_number)

        if all_data:
            if type==1:
                query = query.join(PersonNatural)
            elif type==2:
                query = query.join(PersonLegal)
            
            query = query.options(joinedload(Person.mail.and_(Person.mail.is_active == 1)) if oaf else joinedload(Person.mail))
            query = query.options(joinedload(Person.phone.and_(Person.phone.is_active == 1)) if oaf else joinedload(Person.phone))
            query = query.options(joinedload(Person.address.and_(Person.address.is_active == 1)) if oaf else joinedload(Person.address))
        
        query = query.order_by(order_by if order_by is not None else Person.name.asc())

        print("Final Query:", str(query))

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", limit if limit is not None else 15))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize data
        data = []
        for person in pagination.items:
            person_data = {}
            person_data["person"] = person.to_dict()

            if all_data:
                if type==1:
                    person_data["person_natural"]=person.person_natural.to_dict()
                    person_data["family"]=person.person_natural.family_to_dict()
                    person_data["profession"]=person.person_natural.profession_to_dict()
                elif type==2:
                    person_data["person_legal"]=person.person_legal.to_dict()
            
                # Add related data
                if person.phone:
                    person_data["phones"] = [phone.to_dict() for phone in person.phone]
                if person.mail:
                    person_data["mails"] = [mail.to_dict() for mail in person.mail]
                if person.address:
                    person_data["addresses"] = [address.to_dict() for address in person.address]
           
            data.append(person_data)
        
        return jsonify({
            "items": data,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@person_bp.route("/list", methods=["GET"])
@firebase_auth_required
@swag_from(person_docs["list_person"])
def list_person():
    return get_person(all_data=False)