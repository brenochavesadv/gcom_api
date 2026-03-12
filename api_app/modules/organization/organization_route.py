from main import db
from datetime import datetime
from flask import Blueprint, request
from ...constants.response import RESPONSE, json_response
from ..auth_firebase.firebase_decorators import firebase_auth_required
from flasgger import swag_from
from sqlalchemy.exc import IntegrityError
import traceback
from ..organization.organization_model import Organization

organization_bp = Blueprint("organization", __name__)

@organization_bp.route("/create", methods=["POST"])
@firebase_auth_required
def create_organization():
    try:
        organization_data = request.get_json()
        print("Received organization data:", organization_data)
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
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        if Organization.query.filter_by(uid=uid).first():
            return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)

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
    
        return json_response(uid=new_organization.uid, response="CREATED_SUCCESSFULLY", status_code=201)

    except Exception as e:
        db.session.rollback()
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)


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
        print("Received organization update data:", organization_data)

        if ((uid is None or uid == "") or (name is None or name == "")):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        organization = Organization.query.filter_by(uid=uid).first()
        if not organization:
            return json_response(uid=0, response="NOT_FOUND", status_code=404)
        
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

        return json_response(uid=organization.uid, response="UPDATED_SUCCESSFULLY", status_code=200)

    except IntegrityError as ie:
        db.session.rollback()
        # likely unique/foreign key constraint violation
        print("IntegrityError updating organization:", ie)
        print(traceback.format_exc())
        return json_response(uid=0, response="DUPLICATE_ENTRY", status_code=409)
    
    except Exception as e:
        db.session.rollback()
        print("Error updating organization:", e)
        print(traceback.format_exc())
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@organization_bp.route("/list", methods=["GET"])
@firebase_auth_required
def list_organization():
    try:     
        # Get person_uid from query parameters
        uid = request.args.get("u") 
        main_uid = request.args.get("m")


        if (uid is not None and uid != ""):
            print("Fetching organization by uid:", uid)
            mails = Organization.query.filter_by(uid=uid).first()
        elif (main_uid is not None and main_uid != ""):
            print("Fetching organizations by main_uid:", main_uid)
            mails = Organization.query.filter_by(main_uid_fk=main_uid).all()
        else:
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)
        
        org_list = [Organization.to_dict() for Organization in mails]

        return json_response(uid=0, response="OK", status_code=200, data=org_list)

    except Exception as e:
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)
    
@organization_bp.route("/sync", methods=["GET"])
@firebase_auth_required
def list_organization_for_sync():
    try:     
        # Get person_uid from query parameters
        organization_uid = request.args.get("uid")
        last_update = request.args.get("date")

        if (organization_uid is None or organization_uid == "") or (last_update is None or last_update == ""):
            return json_response(uid=0, response="MISSING_FIELDS", status_code=400)

        org = Organization.query.filter_by(organization_uid_fk=organization_uid)
        org = org.filter(Organization.updated_at > last_update) 
        org = org.all()
        org_list = [org.to_dict() for org in org]

        return json_response(uid=0, response="OK", status_code=200, data=org_list)

    except Exception as e:
        return json_response(uid=0, response="INTERNAL_ERROR", status_code=500)