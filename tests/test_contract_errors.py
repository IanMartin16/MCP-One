from fastapi.testclient import TestClient

from app.config.settings import get_settings
from app.main import app

client = TestClient(app)


def assert_error_contract(body: dict):
    assert "error" in body
    error = body["error"]

    required_fields = {
        "code",
        "message",
        "request_id",
        "details",
    }
    assert required_fields.issubset(error.keys())

    assert isinstance(error["code"], str)
    assert isinstance(error["message"], str)
    assert isinstance(error["request_id"], (str, type(None)))
    assert isinstance(error["details"], dict)


def test_validation_error_contract():
    response = client.post(
        "/orchestrate",
        json={},
    )

    assert response.status_code == 422
    body = response.json()
    assert_error_contract(body)
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_not_found_error_contract():
    response = client.get("/not-a-real-route")

    assert response.status_code == 404
    body = response.json()
    assert_error_contract(body)
    assert body["error"]["code"] == "NOT_FOUND"


def test_route_disabled_error_contract(monkeypatch):
    monkeypatch.setenv("ENABLE_DEBUG_ROUTES", "false")
    get_settings.cache_clear()

    response = client.post(
        "/orchestrate/debug",
        json={
            "user_input": "Help me validate a CURP in Mexico"
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert_error_contract(body)
    assert body["error"]["code"] == "ROUTE_DISABLED"

    get_settings.cache_clear()