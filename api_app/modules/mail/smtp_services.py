import os
from flask import json
from py_smtper import MailManager
from main import root_path

def smtp_info():
    """get smtp info from json file"""

    smtp_options = os.environ.get("SMTP_OPTIONS")
    data = None

    if smtp_options:
        json_path = os.path.expanduser(smtp_options)
        if not os.path.isabs(json_path):
            json_path = os.path.join(root_path, json_path)
        json_path = os.path.abspath(json_path)
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            try:
                data = json.loads(smtp_options)
            except Exception:
                data = None
    else:
        default_path = os.path.join(root_path, "security", "smtp.json")
        if os.path.exists(default_path):
            with open(default_path, "r", encoding="utf-8") as f:
                data = json.load(f)

    smtp_info = {}
    smtp_info["host"] = data.get("host") if isinstance(data, dict) else None
    smtp_info["port"] = data.get("port") if isinstance(data, dict) else None
    smtp_info["username"] = data.get("username") if isinstance(data, dict) else None
    smtp_info["pw"] = data.get("pw") if isinstance(data, dict) else None
    smtp_info["sender"] = data.get("sender") if isinstance(data, dict) else None
    smtp_info["use_ssl"] = data.get("use_ssl") if isinstance(data, dict) else None

    for key, value in smtp_info.items():
        if not value:
            raise RuntimeError(f"SMTP configuration '{key}' is missing in json.")

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
