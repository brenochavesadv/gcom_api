
from backend.apps.commerciall_api import create_app


def test_create_app_registers_health_endpoint():
    app = create_app()

    response = app.test_client().get('/health/test')

    assert response.status_code == 200
    assert response.get_json()['status'] == 'online'
