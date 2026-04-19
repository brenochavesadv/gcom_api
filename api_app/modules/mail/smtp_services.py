import os
from flask import json
from py_smtper import MailManager
from main import root_path

def smtp_info(json_name='smtp.json'):
    """get smtp info from json file"""

    # Corrige o caminho para buscar em ../../../../security/smtp.json
    path = os.path.abspath(os.path.join(root_path, 'security', json_name))
    
    try:    
        with open(path, "r", encoding="utf-8") as f:
            db_info = json.load(f)
            
    except FileNotFoundError:
            raise RuntimeError(f"Database information for {json_name} not found.")

    smtp_info = {}
    smtp_info["host"] = db_info.get("host") if isinstance(db_info, dict) else None
    smtp_info["port"] = db_info.get("port") if isinstance(db_info, dict) else None
    smtp_info["username"] = db_info.get("username") if isinstance(db_info, dict) else None
    smtp_info["pw"] = db_info.get("pw") if isinstance(db_info, dict) else None
    smtp_info["sender"] = db_info.get("sender") if isinstance(db_info, dict) else None
    smtp_info["use_ssl"] = db_info.get("use_ssl") if isinstance(db_info, dict) else None

    for key, value in smtp_info.items():
        if not value:
            raise RuntimeError(f"SMTP configuration '{key}' is missing in {json_name}.")

    return MailManager(
        smtp_server=smtp_info["host"],
        port=smtp_info["port"],
        username=smtp_info["username"],
        password=smtp_info["pw"],
        sender=smtp_info["sender"],
        use_ssl=smtp_info["use_ssl"]
    )   

def send_email_smtp(mail_manager, service_name, body, subject, receiver_email):
    mail_manager.send(service_name=service_name, body=body, subject=subject, receiver_email=receiver_email)
