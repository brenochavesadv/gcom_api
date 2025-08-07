
import pytest
from api_app import create_app, db
from api_app.modules.auth.auth_user_model import AuthUser
from passlib.hash import bcrypt

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            user = AuthUser(username="test", email="test@example.com", hashed_password=bcrypt.hash("123"))
            db.session.add(user)
            db.session.commit()
        yield client

def test_signup_and_login(client):
    response = client.post("/auth/login", json={"username": "test", "password": "123"})
    assert response.status_code == 200
    tokens = response.get_json()
    assert "access_token" in tokens

def test_create_aliquota(client):
    login = client.post("/auth/login", json={"username": "test", "password": "123"})
    token = login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "instit_id_fk": 1,
        "descr": "TX",
        "bematech": "A1",
        "valor": 15.0
    }
    response = client.post("/aliquotas/", json=data, headers=headers)
    assert response.status_code == 201
