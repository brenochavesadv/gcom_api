import json
import os

def db_info(json_name='db_main.json'):
    """get db info from json file"""

    path = os.path.join(os.path.dirname(__file__), "security", json_name)
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

    binds['DB_MAIN'] = 'db_main.json'

    for bind in binds:    

        info = db_info(json_name=binds[bind])
        
        if info:
            key, url = info
            print("Database information loaded successfully: {url}".format(url=url))
            
            if bind == 'DB_MAIN':
                SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{key}@{url}"
                
            SQLALCHEMY_BINDS[bind] = f"mysql+pymysql://{key}@{url}"
            

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecret")
    SWAGGER = {
        'title': "Flask API",
        'uiversion': 3
    }