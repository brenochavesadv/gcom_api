import os
import json
import importlib

from datetime import datetime
from pathlib import Path
from flask import current_app
from backend.modules.utils.api_response import ApiResponse, json_response
from backend.apps.commerciall_api.main import data_path, root_path, env_values


def _resolve_a1_certificate():
    cert_path = os.getenv("A1_CERT_PATH") or env_values.get("A1_CERT_PATH")
    cert_password = os.getenv("A1_CERT_PASSWORD") or env_values.get("A1_CERT_PASSWORD")

    security_folder = Path(root_path) / "security"

    if cert_path:
        cert_file = Path(cert_path)
        if not cert_file.is_absolute():
            cert_file = Path(root_path) / cert_file
    else:
        pfx_files = sorted(security_folder.glob("*.pfx"))
        cert_file = pfx_files[0] if pfx_files else None

    if not cert_file or not cert_file.exists():
        raise FileNotFoundError(
            "A1 certificate (.pfx) not found. Configure A1_CERT_PATH or place a .pfx file in security/."
        )

    if cert_password is None:
        raise RuntimeError("Missing A1_CERT_PASSWORD for A1 certificate authentication.")

    return cert_file, cert_password

def getFromConformidadeFacil(url_param):
    try:

        folder_name = Path(data_path) / f"tax_br_{url_param}"

        date_now = datetime.now().date()
        
        list_files = os.listdir(folder_name) if folder_name.exists() else []

        # the files are stored in the format YYYY-MM-DD.json, so we filter and sort them accordingly
        files = sorted([f for f in list_files if f.endswith(".json")], reverse=True)
        def date_from_filename(filename):
            try:
                return datetime.strptime(filename.split(".")[0], "%Y-%m-%d").date()
            except ValueError:
                return None

        if files:
            latest_file_date = date_from_filename(files[0])
            if latest_file_date and (date_now - latest_file_date).days <= 5:
                json_file = folder_name / files[0]
                loaded_data = None
                with open(json_file, "r", encoding="utf-8") as f:
                    loaded_data = f.read()
                    response_data = json.loads(loaded_data)

                current_app.logger.debug("Conformidade Facil " + url_param + " fetched from local cache file.")

                return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = response_data
                )

        try:
            pkcs12_get = importlib.import_module("requests_pkcs12").get
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Package requests-pkcs12 is required for .pfx certificate authentication. Install requests-pkcs12."
            ) from exc

        cert_file, cert_password = _resolve_a1_certificate()
        cff_url = "https://cff.svrs.rs.gov.br/api/v1/consultas/"+url_param

        # If no recent file is found, fetch from Conformidade Facil API using A1 client certificate
        response = pkcs12_get(
            cff_url,
            headers={
                "Accept": "application/json",
            },
            pkcs12_filename=str(cert_file),
            pkcs12_password=cert_password,
            timeout=60,
        )
        response.raise_for_status()

        json_file = folder_name / f"{date_now.strftime('%Y-%m-%d')}.json"
        folder_name.mkdir(parents=True, exist_ok=True)

        response_data = response.json()

        # Persist last successful response to reduce API calls and tolerate short outages.
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(response_data, f, ensure_ascii=False, indent=4)

        current_app.logger.debug("Conformidade Facil fetched from remote API: "+url_param)

        return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = response_data
                )

    except Exception as e:
        import traceback
        current_app.logger.debug(f"Conformidade Facil list error: {traceback.format_exc()}")
        raise
