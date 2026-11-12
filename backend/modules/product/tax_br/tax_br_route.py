from flask import Blueprint
from ...auth_firebase.firebase_decorators import firebase_auth_required
from .services.siscomex_services import getNcmFromSiscomex
from .services.conformidade_facil_services import getFromConformidadeFacil
from .services.icms_pis_cofins_services import (
    cfop_list_service,
    icms_pis_cofins_list_service,
    upsert_icms_pis_cofins_description_service,
    update_icms_pis_cofins_item_service,
)
from .services.ibs_cbs_services import ibs_cbs_list_service, ibs_cbs_upsert_service
from flask import Blueprint, request


tax_br_bp = Blueprint("tax_br", __name__)

@tax_br_bp.route("/ncm", methods=["GET"])
@firebase_auth_required
def list_ncm():
    return getNcmFromSiscomex()

@tax_br_bp.route("/cst", methods=["GET"])
@firebase_auth_required
def list_cst():
    return getFromConformidadeFacil("classTrib")

@tax_br_bp.route("/cred_presum", methods=["GET"])
@firebase_auth_required
def list_cred_presum():
    return getFromConformidadeFacil("credPresumido")

@tax_br_bp.route("/cfop_list", methods=["GET"])
@firebase_auth_required
def cfop_list():
    return cfop_list_service(request.args.to_dict())

@tax_br_bp.route("/ipc_description", methods=["POST"])
@firebase_auth_required
def ipc_description():
    data = request.get_json() or {}
    return upsert_icms_pis_cofins_description_service(data)

@tax_br_bp.route("/ipc_item", methods=["POST"])
@firebase_auth_required
def ipc_item():
    data = request.get_json() or {}
    return update_icms_pis_cofins_item_service(data)

@tax_br_bp.route("/ipc_list", methods=["GET"])
@firebase_auth_required
def list_icms_pis_cofins():
    uid = request.args.get("u")
    organization_uid_fk = request.args.get("ou")
    return icms_pis_cofins_list_service(uid, organization_uid_fk)

@tax_br_bp.route("/ic_list", methods=["GET"])
@firebase_auth_required
def ibs_cbs_list():
    uid = request.args.get("u")
    organization_uid_fk = request.args.get("ou")
    return ibs_cbs_list_service(uid, organization_uid_fk)


@tax_br_bp.route("/ic_upsert", methods=["POST"])
@firebase_auth_required
def ibs_cbs_upsert():
    data = request.get_json() or {}
    return ibs_cbs_upsert_service(data)