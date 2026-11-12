from types import SimpleNamespace
from unittest.mock import Mock

from flask import Flask

from backend.modules.product.routes import product_route


class FakeProductCfg:
    query = Mock()
    organization_uid_fk = "organization_uid_fk"

    def __init__(self, **values):
        self.__dict__.update(values)

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def to_dict(self):
        return {
            "uid": self.uid,
            "organization_uid_fk": self.organization_uid_fk,
            "default_profit": self.default_profit,
        }


def _route_function(function):
    return getattr(function, "__wrapped__", function)


def _app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


def _config(**overrides):
    values = {
        "uid": "cfg-1",
        "organization_uid_fk": "org-1",
        "default_profit": 10.0,
    }
    values.update(overrides)
    return FakeProductCfg(**values)


def _response_body(result):
    if isinstance(result, tuple):
        response = result[0]
        response.status_code = result[1]
    else:
        response = result
    return response, response.get_json()


def test_get_product_configs_serializes_the_organization_configuration(monkeypatch):
    selected = _config()
    query = Mock()
    query.filter.return_value = query
    query.first.return_value = selected
    monkeypatch.setattr(FakeProductCfg, "query", query)
    monkeypatch.setattr(product_route, "ProductCfg", FakeProductCfg)

    with _app().test_request_context("/product/get_cfg?ou=org-1"):
        result = _route_function(product_route.get_product_configs)()

    response, body = _response_body(result)
    assert response.status_code == 200
    assert body["data"] == {
        "uid": "cfg-1",
        "organization_uid_fk": "org-1",
        "default_profit": 10.0,
    }
    query.filter.assert_called_once()


def test_update_product_configs_updates_the_selected_row(monkeypatch):
    selected = _config()
    query = Mock()
    query.filter_by.return_value = query
    query.first.return_value = selected
    session = SimpleNamespace(commit=Mock(), rollback=Mock())
    monkeypatch.setattr(FakeProductCfg, "query", query)
    monkeypatch.setattr(product_route, "ProductCfg", FakeProductCfg)
    monkeypatch.setattr(product_route, "db", SimpleNamespace(session=session))

    payload = {
        "product_cfg": {
            "uid": "cfg-1",
            "organization_uid_fk": "org-1",
            "default_profit": 15.5,
        }
    }
    with _app().test_request_context("/product/update_cfg", method="PUT", json=payload):
        result = _route_function(product_route.update_product_configs)()

    response, body = _response_body(result)
    assert response.status_code == 200
    assert body["data"]["product_cfg"]["default_profit"] == 15.5
    session.commit.assert_called_once_with()
    assert selected.default_profit == 15.5


def test_update_product_configs_rejects_a_non_object_body(monkeypatch):
    monkeypatch.setattr(product_route, "ProductCfg", FakeProductCfg)

    with _app().test_request_context(
        "/product/update_cfg", method="POST", data="not-json", content_type="text/plain"
    ):
        result = _route_function(product_route.update_product_configs)()

    response, body = _response_body(result)
    assert response.status_code == 400
    assert body["data"]["code"] == "INVALID_JSON"
