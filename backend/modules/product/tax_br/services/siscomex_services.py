import os
import json
import requests

from datetime import datetime
from pathlib import Path
from flask import current_app
from backend.modules.utils.api_response import ApiResponse, json_response
from backend.config import BACKEND_DIR


data_path = BACKEND_DIR / "instance" / "data"

def getNcmFromSiscomex():
    try:

        ncm_folder = Path(data_path) / "tax_br_ncm"

        date_now = datetime.now().date()
        
        list_files = os.listdir(ncm_folder) if ncm_folder.exists() else []

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
                json_file = ncm_folder / files[0]
                ncm_data = None
                with open(json_file, "r", encoding="utf-8") as f:
                    ncm_data = f.read()
                    ncm_data = json.loads(ncm_data)

                print(f"Fetched from file NCM data")  # Debugging line to print the fetched NCM data

                return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = ncm_data
                )

        # If no recent file is found, fetch from the API
        response = requests.get(
            "https://portalunico.siscomex.gov.br/classif/api/publico/nomenclatura/download/json",
            headers={
                "Accept": "application/json",
            },
            timeout=60,
        )

        ncm_file = ncm_folder / f"{date_now.strftime('%Y-%m-%d')}.json"
        ncm_folder.mkdir(parents=True, exist_ok=True)

        # save the json response to a file for debugging
        with open(ncm_file, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)

        print(f"Response status code: {response.status_code}")  # Debugging line to print the response status code
        print(f"Response content: {response.json()}")  # Debugging line to print the response content

        ncm_data = response.json()

        print(f"Fetched from Api NCM data")  # Debugging line to print the fetched NCM data

        return json_response(
                    response = ApiResponse.REQUEST_SUCCESSFUL,
                    data = ncm_data
                )

    except Exception as e:
        import traceback
        current_app.logger.debug(f"Siscomex NCM list error: {traceback.format_exc()}")
        raise
