from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from ..models.person_model import Person
from ..models.person_natural_model import PersonNatural
from ..models.phone_model import Phone
from ..models.mail_model import Mail
from ..models.address_model import Address  
from ..docs.person_natural import person_natural_docs
from ...utils.error_codes import ErrorCodes
from main import db
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from .person_route import get_person

from api_app.modules.person.models import person_model

person_natural_bp = Blueprint("personnatural", __name__)

@person_natural_bp.route("/list", methods=["GET"])
#@firebase_auth_required
@swag_from(person_natural_docs["list_person_natural"])
def list_person_natural():
    return get_person(all_data=True)

@person_natural_bp.route("/new", methods=["POST"])
@firebase_auth_required
@swag_from(person_natural_docs["create_person_natural"])
def new_person_natural():
    print("Creating new person natural...")
    try:
        data = request.get_json()
        person_natural_data = data.get("person_natural", {})

        print('Person Natural Data:', person_natural_data)
        
        # Validate required fields and report which are missing
        required_fields = ["organization_uid_fk", "name", "id_number"]
        missing = [f for f in required_fields if not person_natural_data.get(f)]
        if missing:
            return jsonify({
                "uid": 0,
                "message": "Missing required fields for person natural creation: " + ", ".join(missing),
                "error_code": 2003
            }), 400

        # Check for duplicates BEFORE creating the object
        from sqlalchemy import or_
        # Normalize empty organization UID to None to avoid accidental empty-string matches
        org_uid = person_natural_data.get("organization_uid_fk") or None
        existing = Person.query.filter_by(
            organization_uid_fk=org_uid
        ).filter(
            or_(
                Person.id_number == person_natural_data.get("id_number"),
                Person.name == person_natural_data.get("name")
            )
        ).first()

        if existing:
            return jsonify({
                "message": "(" + str(ErrorCodes.DUPLICATE_ENTRY.code) + ")" + str(ErrorCodes.DUPLICATE_ENTRY.message),
            }), ErrorCodes.DUPLICATE_ENTRY.http_status

        # Create objects using factory
        person = Person.person_data(person_natural_data)
        person.person_uid = None  # Ensure a new record is created
        print(f'Person Data: {person.to_dict()}')   
        db.session.add(person)
        db.session.flush()
        
        person_natural = PersonNatural.person_natural_data(person.person_uid, person_natural_data)
        
        db.session.add(person_natural)
        db.session.commit()
        
        return jsonify({
            "uid": person.person_uid,
            "message": "Person natural created successfully",
            "person": person.to_dict(),
            "person_natural": person_natural.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Person natural creation error: {traceback.format_exc()}")
        return jsonify({
            "uid": 0,
            "error": str(e),
            "error_code": 500
        }), 500

    
@person_natural_bp.route("/update", methods=["PUT"])
@firebase_auth_required
@swag_from(person_natural_docs["update_person_natural"])
def update_person_natural():
    try:
        data = request.get_json()
        person_natural_data = data.get("person_natural", {})

        print('Person Natural Data:', person_natural_data)
        
        # Validate required fields and report which are missing
        required_fields = ["person_uid", "name", "id_number"]
        missing = [f for f in required_fields if not person_natural_data.get(f)]
        if missing:
            return jsonify({
                "uid": 0,
                "message": "Missing required fields for person natural update: " + ", ".join(missing),
                "error_code": 2003
            }), 400

        
        person_data = Person.person_data(person_natural_data)

        # Check if Person exists
        person_record = Person.query.filter_by(person_uid=person_data.person_uid).first()
        if not person_record:
            return jsonify({
                "uid": 0,
                "message": f"Person with ID {person_data.person_uid} not found",
                "error_code": 3001
            }), 404

        # Update the only necessary Person fields 
        person_record.is_active = person_data.is_active
        person_record.is_supplier = person_data.is_supplier
        person_record.name = person_data.name
        person_record.id_number = person_data.id_number
        person_record.credit = person_data.credit
        person_record.balance = person_data.balance

        # Build a temporary PersonNatural object from input to extract values
        temp_person_natural = PersonNatural.person_natural_data(person_data.person_uid, person_natural_data)
        person_natural_record = PersonNatural.query.filter_by(person_uid_fk=person_data.person_uid).first()
        # Check if PersonNatural exists
        if not person_natural_record:
            return jsonify({
                "uid": 0,
                "message": f"PersonNatural with Person ID {person_data.person_uid} not found",
                "error_code": 3001
            }), 404

        # Update PersonNatural fields from the temp object (avoid overwriting PK/FK)
        for key, value in temp_person_natural.to_dict().items():
            if key not in ['person_natural_uid', 'person_uid_fk']:
                setattr(person_natural_record, key, value)

        # Commit all changes
        db.session.commit()

        print(f"Successfully updated Person ID: {person_data.person_uid}")

        # Refresh to get actual database state
        db.session.refresh(person_natural_record)

        return jsonify({
            "uid": person_data.person_uid,
            "message": "Person natural updated successfully",
            "person": person_record.to_dict(),
            "person_natural": person_natural_record.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()  # Important: rollback on error
        import traceback
        print(f"Person natural update error: {traceback.format_exc()}")
        return jsonify({
            "uid": 0,
            "error": str(e),
            "error_code": 500
        }), 500