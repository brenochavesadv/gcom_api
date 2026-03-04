from flask import Blueprint, request, jsonify
from api_app.modules.country.country_model import Country
from datetime import datetime

country_bp = Blueprint("country", __name__)
""" 
@country_bp.route("/", methods=["GET"])
def get_countries():
    try:
        uid = int(request.args.get("uid"))
        iso2Code = request.args.get("iso2Code")
        iso3Code = request.args.get("iso3Code")
        m49Code = request.args.get("m49Code")
        bacenCode = int(request.args.get("bacenCode"))
        phoneCode = int(request.args.get("phoneCode"))
        enUs = request.args.get("enUs")
        ptBr = request.args.get("ptBr")
        esEs = request.args.get("esEs") 
        updated_at = request.args.get("updated_at")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        query = Countries.query
        
        if uid != 0:
            query = query.filter_by(uid=uid)
        elif iso2Code is not None:
            query = query.filter_by(iso2Code=iso2Code)
        elif iso3Code is not None:
            query = query.filter_by(iso3Code=iso3Code)
        elif m49Code is not None:
            query = query.filter_by(m49Code=m49Code)
        elif bacenCode is not None:
            query = query.filter_by(bacenCode=bacenCode)
        elif phoneCode is not None:
            query = query.filter_by(phoneCode=phoneCode)
        elif enUs is not None:  
            query = query.filter(Countries.enUs.ilike(f"%{enUs}%"))
        elif ptBr is not None:
            query = query.filter(Countries.ptBr.ilike(f"%{ptBr}%"))
        elif esEs is not None:
            query = query.filter(Countries.esEs.ilike(f"%{esEs}%"))
        elif updated_at is not None:
            try:
                updated_at_date = datetime.fromisoformat(updated_at)
                query = query.filter(Countries.updated_at >= updated_at_date)
            except ValueError:
                return jsonify({"error": "Invalid date format for updated_at. Use ISO format."}), 400
        else:
            return jsonify({"error": "Required field is empty"}), 200

        pagination = query.order_by(Countries.name.desc()).paginate(page=page, per_page=per_page, error_out=False)

        data = [obj for obj in pagination.items]
        
        return jsonify({
            "items": data,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500 """

def _get_int_arg(name, default):
    val = request.args.get(name, None)
    if val is None or val == "":
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

@country_bp.route("/", methods=["GET"])
def list_countries():
    """List all countries with pagination"""
    try:
        page = _get_int_arg("page", 1)
        per_page = _get_int_arg("per_page", 10)
        
        # Validate pagination
        if page < 1:
            return jsonify({"error": "Page must be greater than 0"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "Per page must be between 1 and 100"}), 400

        pagination = Country.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        countries = [country.to_dict() for country in pagination.items]

        return jsonify({
            "items": countries,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        })
        
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters for countries"}), 400
    except Exception as e:
        import logging
        logging.exception("Error occurred while listing countries")
        return jsonify({"error": f"Database error: {str(e)}"}), 500


