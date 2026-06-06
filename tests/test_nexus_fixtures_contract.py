from fastapi.testclient import TestClient

from app.main import app
from tests.fixture_loader import load_fixture

client = TestClient(app)


def test_resolved_summary_fixture_contract():
    payload = load_fixture("resolved_summary_input.json")

    response = client.post("/orchestrate", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["request_id"] == "nexus-fixture-001"
    assert "status" in body
    assert "mode" in body
    assert "summary" in body
    assert "handoff" in body
    assert "reason_codes" in body


def test_handoff_fixture_contract():
    payload = load_fixture("handoff_input.json")

    response = client.post("/orchestrate", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["request_id"] == "nexus-fixture-002"
    assert "status" in body
    assert "mode" in body
    assert "summary" in body


def test_preview_fixture_contract():
    payload = load_fixture("preview_input.json")

    response = client.post("/orchestrate", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["request_id"] == "nexus-fixture-003"
    assert "status" in body
    assert "mode" in body
    assert "summary" in body


def test_fallback_fixture_contract():
    payload = load_fixture("fallback_input.json")

    response = client.post("/orchestrate", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["request_id"] == "nexus-fixture-004"
    assert "status" in body
    assert "mode" in body
    assert "summary" in body