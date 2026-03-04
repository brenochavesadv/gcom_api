from flask import Blueprint, request, jsonify
from api_app.modules.organization.organization_model import Organization
from api_app.modules.auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
import logging

organization_bp = Blueprint("organization", __name__)

@organization_bp.route("/<int:organization_uid>", methods=["GET"])
@firebase_auth_required()
#@swag_from(organization_docs.get("get_organization", {}))
def get_organization(organization_uid):
    """Get a single organization by ID"""
    try:
        # Validate organization_uid
        if organization_uid <= 0:
            return jsonify({"error": "Invalid organization ID"}), 400

        organization = Organization.query.filter_by(uid=organization_uid).first()

        if organization is None:
            return jsonify({"error": "Organization not found"}), 404

        organization_dict = organization.to_dict()

        # Remove sensitive fields if they exist
        sensitive_fields = ['sensitive_field', 'large_field', 'password', 'secret_key']
        for field in sensitive_fields:
            organization_dict.pop(field, None)
        return jsonify(organization_dict)
        
    except Exception as e:
        logging.exception("Error occurred while fetching organization")
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@organization_bp.route("/", methods=["GET"])
@firebase_auth_required()
def list_organizations():
    """List all organizations with pagination"""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        
        # Validate pagination
        if page < 1:
            return jsonify({"error": "Page must be greater than 0"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "Per page must be between 1 and 100"}), 400
        
        pagination = Organization.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        organizations = [organization.to_dict() for organization in pagination.items]

        return jsonify({
            "items": organizations,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        })
        
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400
    except Exception as e:
        logging.exception("Error occurred while listing organizations")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
