from flask import Blueprint, request, jsonify
from api_app.modules.entity.entity_model import Entity
from api_app.modules.auth_firebase.firebase_decorators import auth_required
from flasgger import swag_from
import logging

entity_bp = Blueprint("entity", __name__)

@entity_bp.route("/<int:entity_id>", methods=["GET"])
#@auth_required()
#@swag_from(entity_docs.get("get_entity", {}))
def get_entity(entity_id):
    """Get a single entity by ID"""
    try:
        # Validate entity_id
        if entity_id <= 0:
            return jsonify({"error": "Invalid entity ID"}), 400
        
        entity = Entity.query.filter_by(id=entity_id).first()
        
        if entity is None:
            return jsonify({"error": "Entity not found"}), 404
        
        entity_dict = entity.to_dict()
        
        # Remove sensitive fields if they exist
        sensitive_fields = ['sensitive_field', 'large_field', 'password', 'secret_key']
        for field in sensitive_fields:
            entity_dict.pop(field, None)
            
        return jsonify(entity_dict)
        
    except Exception as e:
        logging.exception("Error occurred while fetching entity")
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@entity_bp.route("/", methods=["GET"])
#@auth_required()
def list_entities():
    """List all entities with pagination"""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        
        # Validate pagination
        if page < 1:
            return jsonify({"error": "Page must be greater than 0"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "Per page must be between 1 and 100"}), 400
        
        pagination = Entity.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        entities = [entity.to_dict() for entity in pagination.items]
        
        return jsonify({
            "items": entities,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        })
        
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400
    except Exception as e:
        logging.exception("Error occurred while listing entities")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
