from types import SimpleNamespace
import pytest
from flask import Flask

from backend.modules.product.tax_br.services import (
    icms_pis_cofins_services as services,
)
from backend.modules.utils.api_response import ApiResponse


@pytest.fixture
def app():
    application = Flask(__name__)
    application.config.update(TESTING=True)
    return application


@pytest.fixture
def client_context(app):
    with app.app_context():
        yield


class QueryStub:
    def __init__(self, *, rows=None, first_value=None, error=None):
        self.rows = rows or []
        self.first_value = first_value
        self.error = error

    def filter(self, *_args):
        if self.error:
            raise self.error
        return self

    def filter_by(self, **_kwargs):
        if self.error:
            raise self.error
        return self

    def options(self, *_args):
        return self

    def order_by(self, *_args):
        return self

    def all(self):
        if self.error:
            raise self.error
        return self.rows

    def first(self):
        if self.error:
            raise self.error
        return self.first_value


class SessionStub:
    def __init__(self, *, commit_error=None):
        self.added = []
        self.commit_error = commit_error
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


class ModelStub:
    uid = "uid"
    organization_uid_fk = "organization_uid_fk"
    description = "description"

    def __init__(self, **values):
        self.__dict__.update(values)

    def to_dict(self):
        return self.__dict__.copy()


class ItemStub(ModelStub):
    @staticmethod
    def from_json(data):
        return ItemStub(**data)

    def updatable_fields(self, other):
        self.cfop = other.cfop


class _ExpressionStub:
    def asc(self):
        return self


@pytest.fixture(autouse=True)
def replace_orm_models(monkeypatch):
    """Keep these service unit tests independent from mapper configuration."""
    cfop = type("CfopStub", (), {"query": QueryStub(), "cfop": _ExpressionStub()})
    group = type(
        "GroupStub",
        (ModelStub,),
        {
            "query": QueryStub(),
            "uid": _ExpressionStub(),
            "organization_uid_fk": _ExpressionStub(),
            "description": _ExpressionStub(),
        },
    )
    item = type("ItemStubModel", (ItemStub,), {"query": QueryStub()})
    monkeypatch.setattr(services, "Cfop", cfop)
    monkeypatch.setattr(services, "IcmsPisCofinsGroup", group)
    monkeypatch.setattr(services, "IcmsPisCofinsItem", item)


def response_json(result):
    response = result[0] if isinstance(result, tuple) else result
    return response.get_json()


def test_cfop_list_returns_catalog(client_context, monkeypatch):
    rows = [SimpleNamespace(to_dict=lambda: {"cfop": 5102})]
    monkeypatch.setattr(services.Cfop, "query", QueryStub(rows=rows))

    result = services.cfop_list_service()

    body = response_json(result)
    assert body["response"] == ApiResponse.REQUEST_SUCCESSFUL.name
    assert body["data"] == [{"cfop": 5102}]


def test_cfop_list_returns_internal_error(client_context, monkeypatch):
    monkeypatch.setattr(
        services.Cfop,
        "query",
        QueryStub(error=RuntimeError("database unavailable")),
    )

    with pytest.raises(RuntimeError, match="database unavailable"):
        services.cfop_list_service()


def test_group_list_requires_organization(client_context):
    result = services.icms_pis_cofins_list_service(uid=None, organization_uid_fk="")

    assert response_json(result)["response"] == ApiResponse.MISSING_FIELDS.name


def test_group_list_returns_groups(client_context, monkeypatch):
    group = SimpleNamespace(to_dict=lambda: {"uid": "group-1"})
    monkeypatch.setattr(
        services.IcmsPisCofinsGroup,
        "query",
        QueryStub(rows=[group]),
    )

    result = services.icms_pis_cofins_list_service(
        uid=None,
        organization_uid_fk="organization-1",
    )

    assert response_json(result)["data"] == [{"uid": "group-1"}]


def test_get_items_returns_not_found(client_context, monkeypatch):
    monkeypatch.setattr(
        services.IcmsPisCofinsGroup,
        "query",
        QueryStub(first_value=None),
    )

    result = services.icms_pis_cofins_get_items_service("group-1")

    body = response_json(result)
    assert body["response"] == ApiResponse.NO_DATA.name
    assert body["data"]["error"] == "Icms Pis Cofins group not found"


def test_get_items_returns_group(client_context, monkeypatch):
    group = SimpleNamespace(to_dict=lambda: {"uid": "group-1", "items": []})
    monkeypatch.setattr(
        services.IcmsPisCofinsGroup,
        "query",
        QueryStub(first_value=group),
    )

    result = services.icms_pis_cofins_get_items_service("group-1")

    assert response_json(result)["data"] == {"uid": "group-1", "items": []}


def test_group_upsert_requires_organization_and_description(client_context):
    result = services.upsert_icms_pis_cofins_description_service(
        {"uid": "0", "ou": "", "description": ""}
    )

    assert response_json(result)["response"] == ApiResponse.MISSING_FIELDS.name


def test_group_upsert_updates_existing_group(client_context, monkeypatch):
    group = ModelStub(uid="group-1", description="Old")
    session = SessionStub()
    monkeypatch.setattr(
        services.IcmsPisCofinsGroup,
        "query",
        QueryStub(first_value=group),
    )
    monkeypatch.setattr(services, "db", SimpleNamespace(session=session))

    result = services.upsert_icms_pis_cofins_description_service(
        {"uid": "group-1", "ou": "organization-1", "description": "New"}
    )

    body = response_json(result)
    assert body["response"] == ApiResponse.UPDATED_SUCCESSFULLY.name
    assert group.description == "New"
    assert session.commits == 1


def test_group_upsert_creates_group_and_default_items(client_context, monkeypatch):
    session = SessionStub()
    monkeypatch.setattr(ModelStub, "query", QueryStub(first_value=None), raising=False)
    monkeypatch.setattr(services, "IcmsPisCofinsGroup", ModelStub)
    monkeypatch.setattr(services, "IcmsPisCofinsItem", ItemStub)
    monkeypatch.setattr(services, "db", SimpleNamespace(session=session))

    result = services.upsert_icms_pis_cofins_description_service(
        {"uid": "0", "ou": "organization-1", "description": "General goods"}
    )

    body = response_json(result)
    assert body["response"] == ApiResponse.CREATED_SUCCESSFULLY.name
    assert len(session.added) == 7
    assert session.commits == 1


def test_group_upsert_rolls_back_on_commit_error(client_context, monkeypatch):
    session = SessionStub(commit_error=RuntimeError("write failed"))
    monkeypatch.setattr(
        services.IcmsPisCofinsGroup,
        "query",
        QueryStub(first_value=ModelStub(uid="group-1")),
    )
    monkeypatch.setattr(services, "db", SimpleNamespace(session=session))

    with pytest.raises(RuntimeError, match="write failed"):
        services.upsert_icms_pis_cofins_description_service(
            {"uid": "group-1", "ou": "organization-1", "description": "New"}
        )
    assert session.rollbacks == 1


def test_item_upsert_requires_group(client_context):
    result = services.upsert_icms_pis_cofins_item_service(
        {"icmsPisCofinsItem": {"icms_pis_cofins_group_uid_fk": ""}, "cfopType": "cfop_sell_same_uf"}
    )

    assert response_json(result)["response"] == ApiResponse.MISSING_FIELDS.name


def test_item_upsert_returns_not_found_for_unknown_group(client_context, monkeypatch):
    monkeypatch.setattr(
        services.IcmsPisCofinsGroup,
        "query",
        QueryStub(first_value=None),
    )

    result = services.upsert_icms_pis_cofins_item_service(
        {
            "icmsPisCofinsItem": {
                "uid": "item-1",
                "icms_pis_cofins_group_uid_fk": "missing-group",
            },
            "cfopType": "cfop_sell_same_uf",
        }
    )

    assert response_json(result)["response"] == ApiResponse.NOT_FOUND.name


def test_item_upsert_updates_existing_item(client_context, monkeypatch):
    group = ModelStub(uid="group-1")
    item = ItemStub(uid="item-1", cfop=100)
    incoming = {
        "uid": "item-1",
        "icms_pis_cofins_group_uid_fk": "group-1",
        "cfop": 5102,
    }
    session = SessionStub()
    monkeypatch.setattr(services.IcmsPisCofinsGroup, "query", QueryStub(first_value=group))
    monkeypatch.setattr(services.IcmsPisCofinsItem, "query", QueryStub(first_value=item))
    monkeypatch.setattr(services, "db", SimpleNamespace(session=session))

    result = services.upsert_icms_pis_cofins_item_service(
        {"icmsPisCofinsItem": incoming, "cfopType": "cfop_sell_same_uf"}
    )

    assert response_json(result)["response"] == ApiResponse.UPDATED_SUCCESSFULLY.name
    assert item.cfop == 5102
    assert group.cfop_sell_same_uf_item_uid_fk == "item-1"
    assert session.commits == 1


def test_item_upsert_rolls_back_on_error(client_context, monkeypatch):
    session = SessionStub(commit_error=RuntimeError("write failed"))
    group = ModelStub(uid="group-1")
    monkeypatch.setattr(services.IcmsPisCofinsGroup, "query", QueryStub(first_value=group))
    monkeypatch.setattr(services.IcmsPisCofinsItem, "query", QueryStub(first_value=None))
    monkeypatch.setattr(services, "db", SimpleNamespace(session=session))

    with pytest.raises(RuntimeError, match="write failed"):
        services.upsert_icms_pis_cofins_item_service(
            {
                "icmsPisCofinsItem": {
                    "uid": "0",
                    "icms_pis_cofins_group_uid_fk": "group-1",
                    "cfop": 5102,
                },
                "cfopType": "cfop_sell_same_uf",
            }
        )
    assert session.rollbacks == 1
