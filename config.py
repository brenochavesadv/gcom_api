import json
import os
from main import root_path
from dotenv import dotenv_values

def db_info(json_name='db_main.json'):
    """get db info from json file in production environment"""

    path = os.path.join(root_path, "security", json_name)
    try:    
        with open(path, "r", encoding="utf-8") as f:
            db_info = json.load(f)
    except FileNotFoundError:
            raise RuntimeError(f"Database information for {json_name} not found.")

    key = db_info.get("key") if isinstance(db_info, dict) else None
    url = db_info.get("url") if isinstance(db_info, dict) else None

    if not key or not url:
        raise RuntimeError("Database missing in the provided information.")

    return key, url

class Config:

    binds = {}
    SQLALCHEMY_BINDS = {}

    env_values = dotenv_values(dotenv_path=os.path.join(root_path, ".env"))
    environment_mode = env_values.get("FLASK_ENV", "development")
    print(f"Running in {environment_mode} environment.")

    if environment_mode == "production":

        binds['DB_MAIN'] = 'db_main.json'
        binds['DB_FROTALL'] = 'db_frotall.json'

        for bind in binds:    

            info = db_info(json_name=binds[bind])
            
            if info:
                key, url = info
                print("Database information loaded successfully: {url}".format(url=url))
                
                if bind == 'DB_MAIN':
                    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{key}@{url}"
                    
                SQLALCHEMY_BINDS[bind] = f"mysql+pymysql://{key}@{url}"

    else:

        path = os.path.join(root_path, "security", "db_development.json")
        try:    
            with open(path, "r", encoding="utf-8") as f:
                db_info = json.load(f)
        except FileNotFoundError:
                raise RuntimeError(f"Development Database information not found: db_development.json")

        key = db_info.get("key") if isinstance(db_info, dict) else None
        url_main = db_info.get("url_main") if isinstance(db_info, dict) else None
        url_frotall = db_info.get("url_frotall") if isinstance(db_info, dict) else None

        if not key or not url_main:
            raise RuntimeError("Development Database missing in the provided information.")

        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{key}@{url_main}"
        SQLALCHEMY_BINDS['DB_MAIN'] = f"mysql+pymysql://{key}@{url_main}"
        SQLALCHEMY_BINDS['DB_FROTALL'] = f"mysql+pymysql://{key}@{url_frotall}"

        print("Database information loaded successfully for development: {url}".format(url=url_main))

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecret")
    SWAGGER = {
        'title': "Flask API",
        'uiversion': 3
    }