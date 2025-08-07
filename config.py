import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    #SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://avantz0101_add1:avantz0101_dev@avantz.com.br:3306/avantz01")
    #SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://brtecno02:brtecno02dev@brtecno.com.br:3306/financiall")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:Bj150181@localhost:3306/avantz_local")
    
    # Change SQLALCHEMY_DATABASE_BINDS to SQLALCHEMY_BINDS
    SQLALCHEMY_BINDS = {
        #'main': os.getenv("PERSON_DATABASE_URL", "mysql+pymysql://brtecno02:brtecno02dev@brtecno.com.br:3306/db1"),
        'main': os.getenv("MAIN_DATABASE_URL", "mysql+pymysql://root:Bj150181@localhost:3306/avantz_local"),
        'product': os.getenv("PERSON_DATABASE_URL", "mysql+pymysql://root:Bj150181@localhost:3306/product"),
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecret")
    SWAGGER = {
        'title': "Flask API",
        'uiversion': 3
    }