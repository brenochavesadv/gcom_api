from datetime import datetime
from flask import Blueprint, request, jsonify
from ..models.person_control import PersonControl
from ..models.person_natural import PersonNatural
from ..models.phones import Phones
from ..models.mails import Mails
from ..models.address import Address  
from ..docs.person_natural import person_natural_docs
from main import db
from ...auth_firebase.firebase_decorators import auth_required
from flasgger import swag_from
from sqlalchemy.orm import selectinload,joinedload

person_natural_bp = Blueprint("personnatural", __name__)

@person_natural_bp.route("/list", methods=["GET"])
#@auth_required
@swag_from(person_natural_docs["list_person_natural"])
def list_person_natural():
    try:
        # Get parameters
        id = request.args.get("id")
        name = request.args.get("name")
        is_active = request.args.get("is_active") 
        is_supplier = request.args.get("is_supplier")
        type_ = request.args.get("type")
        entity_id = request.args.get("entity_id")
        id_number = request.args.get("id_number")
        only_active_fields = request.args.get("oaf")

        if entity_id is None:
            return jsonify({"error": "Entity ID is required"}), 400      
        
        query = PersonControl.query.filter(PersonControl.entity_id_fk == entity_id)
        query = query.join(PersonNatural)
        
        # Apply filters
        if id is not None:
            query = query.filter(PersonControl.id == int(id))
        if name is not None:
            query = query.filter(PersonControl.name.ilike(f"%{name}%"))
        if is_active is not None and only_active_fields != "true":
            is_active_bool = True if is_active.lower() == "true" else False
            query = query.filter(PersonControl.is_active == is_active_bool)
        if is_supplier is not None:
            is_supplier_bool = True if is_supplier.lower() == "true" else False
            query = query.filter(PersonControl.is_supplier == is_supplier_bool)
        if type_ is not None:
            query = query.filter(PersonControl.person_type == int(type_))
        if id_number is not None:
            query = query.filter(PersonControl.id_number == id_number)

        if only_active_fields == "true":

            query = query.filter(PersonControl.is_active == True)
            query = query.options(joinedload(PersonControl.mails.and_(Mails.is_active == True)))
            query = query.options(joinedload(PersonControl.phones.and_(Phones.is_active == True)))
            query = query.options(joinedload(PersonControl.addresses.and_(Address.is_active == True)))

        query = query.order_by(PersonControl.name.desc())

        # Pagination
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Serialize data
        data = []
        for person_control in pagination.items:
            control_data = person_control.to_dict()
            
            # Add related data
            if person_control.person_natural:
                control_data["natural_info"] = person_control.person_natural.to_dict()
            if person_control.phones:
                control_data["phones"] = [phone.to_dict() for phone in person_control.phones]
            if person_control.mails:
                control_data["mails"] = [mail.to_dict() for mail in person_control.mails]
            if person_control.addresses:
                control_data["addresses"] = [address.to_dict() for address in person_control.addresses]

            data.append(control_data)
        
        return jsonify({
            "items": data,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages
        })

    except Exception as e:
        import traceback
        print(f"Person natural list error: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

