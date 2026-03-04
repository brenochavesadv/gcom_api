import json
import os

def db_info():
    """get db info from json file"""

    json_url = os.environ.get('INFO_DB')

    if json_url:
        path = os.path.expanduser(json_url)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                db_info = json.load(f)
        else:
            try:
                db_info = json.loads(json_url)
            except Exception:
                db_info = None
                raise RuntimeError("Database information not found.")

    key = db_info.get("key") if isinstance(db_info, dict) else None
    url = db_info.get("url") if isinstance(db_info, dict) else None

    if not key or not url:
        raise RuntimeError("Database missing in the provided information.")

    return key, url


class Config:

    FLASK_ENV = os.getenv("FLASK_ENV", "production")

    info = db_info()
    if info:
        key, url = info
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{key}@{url}"
    else:
        raise RuntimeError("Database information not loaded.")

    # Change SQLALCHEMY_DATABASE_BINDS to SQLALCHEMY_BINDS
    SQLALCHEMY_BINDS = {
        #'main': os.getenv("PERSON_DATABASE_URI", "mysql+pymysql://brtecno02:brtecno02dev@brtecno.com.br:3306/db1"),
        #'main': os.getenv("MAIN_DATABASE_URI", "mysql+pymysql://  /avantz_main"),
        'sales': os.getenv("SALES_DATABASE_URI", "mysql+pymysql://avantz_add1:Ben4L7clsS4A@mysql.avantz.com.br:3306/avantz"),
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecret")
    SWAGGER = {
        'title': "Flask API",
        'uiversion': 3
    }