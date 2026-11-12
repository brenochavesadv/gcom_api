from types import SimpleNamespace

import pytest
from flask import Flask, request

from backend.modules.person.services import person_services as services
from backend.modules.utils.error_handlers import register_error_handlers
from backend.modules.utils.api_response import ApiResponse


class PaginationStub:
    def __init__(self, items):
        self.items = items
        self.total = len(items)
        self.page = 1
        self.pages = 1


class QueryStub:
    def __init__(self, *, rows=None, first_value=None, error=None):
        self.rows = rows or []
        self.first_value = first_value
        self.error = error

    def _raise_if_needed(self):
        if self.error:
            raise self.error

    def filter(self, *_args):
        self._raise_if_needed()
        return self

    def filter_by(self, **_kwargs):
        self._raise_if_needed()
        return self

    def options(self, *_args):
        self._raise_if_needed()
        return self

    def order_by(self, *_args):
        self._raise_if_needed()
        return self

    def join(self, *_args):
        self._raise_if_needed()
        return self

    def distinct(self):
        self._raise_if_needed()
        return self

    def paginate(self, **_kwargs):
        self._raise_if_needed()
        return PaginationStub(self.rows)

    def first(self):
        self._raise_if_needed()
        return self.first_value


class SessionStub:
    def __init__(self, *, commit_error=None):
        self.commit_error = commit_error
        self.added = []
        self.commits = 0
        self.rollbacks = 0

    def add(self, value):
        self.added.append(value)

    def commit(self):
        if self.commit_error:
            raise self.commit_error
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class ColumnStub:
    def __eq__(self, _other):
        return self

    def ilike(self, _pattern):
        return self

    def asc(self):
        return self


class PersonGatewayStub:
    uid = ColumnStub()
    name = ColumnStub()
    id_number = ColumnStub()
    person_type = ColumnStub()
    main_organization_uid_fk = ColumnStub()

    def __init__(self, query):
        self.query = query


def response_json(result):
    response = result[0] if isinstance(result, tuple) else result
    return response.get_json()


@pytest.fixture
def app(monkeypatch):
    app = Flask(__name__)
    app.config.update(TESTING=True)
    register_error_handlers(app)
    monkeypatch.setattr(services, "current_app", app, raising=False)
    with app.app_context():
        yield app


def test_person_list_requires_organization_and_person_type(app):
    with app.test_request_context("/person/list"):
        result = services.person_list({"mou": "1"})

    body = response_json(result)
    assert body["response"] == ApiResponse.MISSING_FIELDS.name
    assert result[1] == ApiResponse.MISSING_FIELDS.http_status


def test_person_list_returns_serialized_people(app, monkeypatch):
    person = SimpleNamespace(
        to_dict=lambda: {"uid": "person-1", "name": "Ana"},
        phone=[],
        mail=[],
        address=[],
        person_accounts=[],
        person_financial=None,
        person_patrimony=[],
    )
    monkeypatch.setattr(services, "Person", PersonGatewayStub(QueryStub(rows=[person])))

    with app.test_request_context("/person/list?page=1&per_page=15"):
        result = services.person_list({"mou": "1", "pt": "1"})

    body = response_json(result)
    assert result[1] == ApiResponse.REQUEST_SUCCESSFUL.http_status
    assert body["data"] == [{"person": {"uid": "person-1", "name": "Ana"}}]
    assert body["extra"]["total"] == 1


def test_person_list_propagates_unexpected_errors_to_global_handler(app, monkeypatch):
    monkeypatch.setattr(
        services,
        "Person",
        PersonGatewayStub(QueryStub(error=RuntimeError("database unavailable"))),
    )

    @app.get("/person-list")
    def list_route():
        return services.person_list({"mou": "1", "pt": "1"})

    # The real database session is not initialized in this unit test.
    monkeypatch.setattr(
        "backend.modules.utils.error_handlers._rollback",
        lambda: None,
    )

    response = app.test_client().get("/person-list")

    assert response.status_code == ApiResponse.INTERNAL_ERROR.http_status
    body = response.get_json()
    assert body["response"] == ApiResponse.INTERNAL_ERROR.name
    assert body["extra"]["exception"] == "RuntimeError"
    assert "database unavailable" not in response.get_data(as_text=True)


def test_person_upsert_returns_missing_fields_without_writing(app, monkeypatch):
    person_data = SimpleNamespace(
        uid=None,
        main_organization_uid_fk=None,
        name=None,
        id_number=None,
        person_type=None,
    )
    class PersonInputStub(PersonGatewayStub):
        @staticmethod
        def from_json(_data):
            return person_data

    monkeypatch.setattr(services, "Person", PersonInputStub(QueryStub()))

    with app.test_request_context("/person", method="POST", json={}):
        result = services.person_upsert()

    body = response_json(result)
    assert body["response"] == ApiResponse.MISSING_FIELDS.name


def test_person_upsert_rolls_back_and_global_handler_maps_commit_error(app, monkeypatch):
    person_data = SimpleNamespace(
        uid="person-1",
        main_organization_uid_fk="organization-1",
        name="Ana",
        id_number="123",
        person_type=1,
        is_active=1,
        is_supplier=False,
        iso2alpha="BR",
        to_dict=lambda: {"uid": "person-1"},
    )
    session = SessionStub(commit_error=RuntimeError("write failed"))

    class PersonInputStub(PersonGatewayStub):
        @staticmethod
        def from_json(_data):
            return person_data

    monkeypatch.setattr(
        services,
        "Person",
        PersonInputStub(QueryStub(first_value=person_data)),
    )
    monkeypatch.setattr(services.PersonFinancial, "from_json", lambda _data: None)
    monkeypatch.setattr(services.PersonNatural, "from_json", lambda _data: None)
    monkeypatch.setattr(services.PersonSupplementary, "from_json", lambda _data: None)
    monkeypatch.setattr(services.PersonLegal, "from_json", lambda _data: None)
    monkeypatch.setattr(services, "db", SimpleNamespace(session=session))
    monkeypatch.setattr(
        "backend.modules.utils.error_handlers._rollback",
        lambda: None,
    )

    @app.post("/person-upsert")
    def upsert_route():
        return services.person_upsert()

    response = app.test_client().post("/person-upsert", json={})

    assert response.status_code == ApiResponse.INTERNAL_ERROR.http_status
    assert response.get_json()["extra"]["exception"] == "RuntimeError"
    assert session.commits == 0
