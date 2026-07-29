from main import db
from datetime import datetime
from flask import Blueprint, current_app, request
from ...utils.api_response import ApiResponse, json_response
from ...auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from sqlalchemy.exc import IntegrityError
import traceback
from ..models.organization_model import Organization

organization_bp = Blueprint("organization", __name__)

@organization_bp.route("/create", methods=["POST"])
@firebase_auth_required
def create_organization():
    try:
        organization_data = request.get_json()
        current_app.logger.debug("Received organization data:", organization_data)
        uid = organization_data.get("uid")
        main_organization_uid = organization_data.get("main_organization_uid")
        is_active = organization_data.get("is_active")
        name = organization_data.get("name")
        phone = organization_data.get("phone")
        mail = organization_data.get("mail")
        site = organization_data.get("site")
        address = organization_data.get("address")
        address_number = organization_data.get("address_number")
        address_complement = organization_data.get("address_complement")
        neighborhood = organization_data.get("neighborhood")
        city = organization_data.get("city")
        state = organization_data.get("state")
        zip_code = organization_data.get("zip_code")
        country = organization_data.get("country")
        instagram = organization_data.get("instagram")
        facebook = organization_data.get("facebook")
        picture = organization_data.get("picture")
        slogan = organization_data.get("slogan")
        active_modules = organization_data.get("active_modules")
        sync_status = organization_data.get("sync_status")

        if ((uid is None or uid == "") or (name is None or name == "")):
            return json_response(response=ApiResponse.MISSING_FIELDS)

        if Organization.query.filter_by(uid=uid).first():
            return json_response(response=ApiResponse.DUPLICATE_ENTRY)

        new_organization = Organization(
            uid=uid,
            main_organization_uid=main_organization_uid,
            name=name,
            phone=phone,
            mail=mail,
            site=site,
            address=address,
            address_number=address_number,
            address_complement=address_complement,
            neighborhood=neighborhood,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country,
            instagram=instagram,
            facebook=facebook,
            picture=picture,
            slogan=slogan,
            active_modules=active_modules,
            is_active=1 if is_active else 0,
            sync_status=sync_status,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.session.add(new_organization)
        db.session.commit()
    
        return json_response(response=ApiResponse.CREATED_SUCCESSFULLY, data={"organization": new_organization.to_dict()})

    except Exception as e:
        db.session.rollback()
        return json_response(response=ApiResponse.INTERNAL_ERROR)


@organization_bp.route("/update", methods=["PUT"])
@firebase_auth_required
def update_organization():
    try:
        organization_data = request.get_json()
        uid = organization_data.get("uid")
        main_organization_uid = organization_data.get("main_organization_uid")
        is_active = organization_data.get("is_active")
        name = organization_data.get("name")
        phone = organization_data.get("phone")
        mail = organization_data.get("mail")
        site = organization_data.get("site")
        address = organization_data.get("address")
        address_number = organization_data.get("address_number")
        address_complement = organization_data.get("address_complement")
        neighborhood = organization_data.get("neighborhood")
        city = organization_data.get("city")
        state = organization_data.get("state")
        zip_code = organization_data.get("zip_code")
        country = organization_data.get("country")
        instagram = organization_data.get("instagram")
        facebook = organization_data.get("facebook")
        picture = organization_data.get("picture")
        slogan = organization_data.get("slogan")
        active_modules = organization_data.get("active_modules")
        sync_status = organization_data.get("sync_status")
        current_app.logger.debug("Received organization update data:", organization_data)

        if ((uid is None or uid == "") or (name is None or name == "")):
            return json_response(response=ApiResponse.MISSING_FIELDS)

        organization = Organization.query.filter_by(uid=uid).first()
        if not organization:
            return json_response(response=ApiResponse.NOT_FOUND)

        if is_active is not None:
            organization.is_active = 1 if is_active else 0
        organization.name = name
        organization.phone = phone
        organization.mail = mail
        organization.site = site
        organization.address = address
        organization.address_number = address_number
        organization.address_complement = address_complement
        organization.neighborhood = neighborhood
        organization.city = city
        organization.state = state
        organization.zip_code = zip_code
        organization.country = country
        organization.instagram = instagram
        organization.facebook = facebook
        organization.picture = picture
        organization.slogan = slogan
        organization.active_modules = active_modules
        organization.sync_status = sync_status
        organization.updated_at = datetime.now()

        db.session.commit()

        return json_response(response=ApiResponse.UPDATED_SUCCESSFULLY, data={"organization": organization.to_dict()})

    except IntegrityError as ie:
        db.session.rollback()
        # likely unique/foreign key constraint violation
        current_app.logger.debug("IntegrityError updating organization:", ie)
        current_app.logger.debug(traceback.format_exc())
        return json_response(response=ApiResponse.DUPLICATE_ENTRY)
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.debug("Error updating organization:", e)
        current_app.logger.debug(traceback.format_exc())
        return json_response(response=ApiResponse.INTERNAL_ERROR)
    
@organization_bp.route("/list", methods=["GET"])
@firebase_auth_required
def list_organization(): 

    try:     
        # Get person_uid from query parameters
        uid = request.args.get("u")
        name = request.args.get("n")
        limit = request.args.get("limit")  # limit of items per page
        order_by = request.args.get("order")  # field to order by

        org_query = Organization.query

        if (uid is not None and uid != ""):
            current_app.logger.debug("Fetching organizations by uid:", uid)
            org_query = org_query.filter_by(uid=uid)
        elif (name is not None and name != ""):
            current_app.logger.debug("Fetching organizations by name:", name)
            org_query = org_query.filter(Organization.name.ilike(f"%{name}%"))
        else:
            return json_response(response=ApiResponse.MISSING_FIELDS)

        org_query = org_query.order_by(order_by if order_by is not None else Organization.name.asc())

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", limit if limit is not None else 15))
        pagination = org_query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize data
        data = []
        for org in pagination.items:           
            data.append(org.to_dict())
        
        return json_response(
            response = ApiResponse.OK,
            data = data,
            total = pagination.total,
            page = pagination.page,
            pages = pagination.pages
        )

    except Exception as e:
        current_app.logger.debug("Error listing organizations:", e)
        current_app.logger.debug(traceback.format_exc())
        return json_response(response=ApiResponse.INTERNAL_ERROR)

@organization_bp.route("/sync", methods=["GET"])
@firebase_auth_required
def list_organization_for_sync():
    try:     
        # Get person_uid from query parameters
        organization_uid = request.args.get("uid")
        last_update = request.args.get("date")

        if (organization_uid is None or organization_uid == "") or (last_update is None or last_update == ""):
            return json_response(response=ApiResponse.MISSING_FIELDS)

        org = Organization.query.filter_by(organization_uid_fk=organization_uid)
        org = org.filter(Organization.updated_at > last_update) 
        org = org.all()
        org_list = [org.to_dict() for org in org]

        return json_response(response=ApiResponse.OK, data=org_list)

    except Exception as e:
        return json_response(response=ApiResponse.INTERNAL_ERROR)