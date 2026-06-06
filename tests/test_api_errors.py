from app.config.settings import get_settings


def test_validation_error_shape(client):
    response = client.post(
        "/orchestrate",
        json={},
    )

    assert response.status_code == 422
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "message" in body["error"]
    assert "details" in body["error"]


def test_debug_disabled_error_shape(client, monkeypatch):
    monkeypatch.setenv("ENABLE_DEBUG_ROUTES", "false")
    get_settings.cache_clear()

    response = client.post(
        "/orchestrate/debug",
        json={"user_input": "Help me validate a CURP in Mexico"},
    )

    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "ROUTE_DISABLED"

    get_settings.cache_clear()


def test_not_found_error_shape(client):
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "NOT_FOUND"