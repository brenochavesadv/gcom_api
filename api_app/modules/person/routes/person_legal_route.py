from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

from api_app.modules.person.routes.person_route import get_person
from ..models.person_model import Person
from ..models.person_legal_model import PersonLegal
from ..models.phone_model import Phone
from ..models.mail_model import Mail
from ..models.address_model import Address  
from ...utils.error_codes import ErrorCodes
from main import db
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from sqlalchemy.orm import selectinload,joinedload

from api_app.modules.person.models import person_model

person_legal_bp = Blueprint("PersonLegal", __name__)

@person_legal_bp.route("/list", methods=["GET"])
@firebase_auth_required
#@swag_from(person_legal_docs["list_person_legal"])
def list_person_legal():
    return get_person(all_data=True)


@person_legal_bp.route("/new", methods=["POST"])
@firebase_auth_required
#@swag_from(person_legal_docs["create_person_legal"])
def new_person_legal():
    try:
        data = request.get_json()
        print(f"data received: {data}")
        person_legal_data = data.get("person_legal", {})
        
        # Validate required fields using factory
        if (not person_legal_data.get("organization_uid_fk") 
            or not person_legal_data.get("name") 
            or not person_legal_data.get("id_number")):
            return jsonify({
                "uid": 0,
                "message": "Missing required fields",
                "error_code": 2003
            }), 400

        # Check for duplicates BEFORE creating the object
        from sqlalchemy import or_
        existing = Person.query.filter_by(
            organization_uid_fk=person_legal_data.get("organization_uid_fk")
        ).filter(
            or_(
                Person.id_number == person_legal_data.get("id_number"),
                Person.name == person_legal_data.get("name")
            )
        ).first()

        if existing:
            return jsonify({
                "message": "(" + str(ErrorCodes.DUPLICATE_ENTRY.code) + ")" + str(ErrorCodes.DUPLICATE_ENTRY.message),
            }), ErrorCodes.DUPLICATE_ENTRY.http_status

        # Create objects using factory
        person = Person.from_json(person_legal_data)
        person.person_uid = None  # Ensure UID is None for new record
        print(f'Person Data: {person.to_dict()}')   
        db.session.add(person)
        db.session.flush()

        person_legal = PersonLegal.from_json(person.person_uid, person_legal_data)
        
        db.session.add(person_legal)
        db.session.commit()
        
        return jsonify({
            "uid": person.person_uid,
            "message": "Person legal created successfully",
            "person": person.to_dict(),
            "person_legal": person_legal.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Person legal creation error: {traceback.format_exc()}")
        return jsonify({
            "uid": 0,
            "error": str(e),
            "error_code": 500
        }), 500

    
@person_legal_bp.route("/update", methods=["PUT"])
@firebase_auth_required
#@swag_from(person_legal_docs["update_person_legal"])
def update_person_legal():
    try:
        data = request.get_json()
        print(f"data received: {data}")

        # Extract data from nested structure
        person_data = data.get("person", {})
        person_legal_data = data.get("person_legal", {})
        
        # Clean datetime fields to avoid MySQL errors
        def clean_data_for_update(data_dict):
            """Clean data for update operations"""
            cleaned = data_dict.copy()
            
            # Remove created_at - should never be updated
            cleaned.pop("created_at", None)
            
            # Remove empty datetime strings that cause MySQL errors
            datetime_fields = ['updated_at', 'person_create_at']
            for field in datetime_fields:
                if field in cleaned and cleaned[field] == '':
                    del cleaned[field]
            
            return cleaned

        # Clean both data dictionaries
        person_data = clean_data_for_update(person_data)
        person_legal_data = clean_data_for_update(person_legal_data)

        # Verify required fields
        if not person_data.get("uid"):
            return jsonify({
                "uid": 0,
                "message": "Missing required field: uid",
                "error_code": 2003
            }), 400

        person_id = person_data.get("uid")
        
        # Check if Person exists
        existing = Person.query.get(person_id)
        if not existing:
            return jsonify({
                "uid": 0,
                "message": f"Person with ID {person_id} not found",
                "error_code": 3001
            }), 404

        # Update Person fields directly on existing object
        for field, value in person_data.items():
            if hasattr(existing, field) and field != 'uid':
                setattr(existing, field, value)
        
        existing.updated_at = datetime.now()

        # Handle PersonLegal
        existing_legal = PersonLegal.query.filter_by(
            person_uid_fk=person_id
        ).first()

        if existing_legal:
            # Update existing PersonLegal
            for field, value in person_legal_data.items():
                if hasattr(existing_legal, field) and field not in ['uid']:
                    setattr(existing_legal, field, value)
            
        else:
            # Create new PersonLegal if it doesn't exist
            person_legal_data['person_uid_fk'] = person_id
            
            # Remove any fields that shouldn't be set
            person_legal_data.pop('uid', None)
            
            existing_legal = PersonLegal(**person_legal_data)
            db.session.add(existing_legal)

        # Commit all changes
        db.session.commit()

        print(f"Successfully updated Person UID: {existing.person_uid}")

        return jsonify({
            "uid": existing.person_uid,
            "message": "Person legal updated successfully",
            "person": existing.to_dict(),
            "person_legal": existing_legal.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()  # Important: rollback on error
        import traceback
        print(f"Person legal update error: {traceback.format_exc()}")
        return jsonify({
            "uid": 0,
            "error": str(e),
            "error_code": 500
        }), 500