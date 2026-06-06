from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_orchestrate_contract_shape():
    response = client.post(
        "/orchestrate",
        json={
            "user_input": "Help me validate a CURP in Mexico",
            "client_context": {
                "source": "nexus",
                "channel": "widget",
                "session_id": "sess-contract-001",
            },
            "request_id": "nexus-contract-001",
        },
    )

    assert response.status_code == 200
    body = response.json()

    required_fields = {
        "request_id",
        "status",
        "mode",
        "modules_used",
        "capabilities_used",
        "summary",
        "handoff",
        "restrictions",
        "confidence",
        "matched_patterns",
        "reason_codes",
    }

    assert required_fields.issubset(body.keys())

    assert isinstance(body["request_id"], (str, type(None)))
    assert isinstance(body["status"], (str, type(None)))
    assert isinstance(body["mode"], str)
    assert isinstance(body["modules_used"], list)
    assert isinstance(body["capabilities_used"], list)
    assert isinstance(body["summary"], str)
    assert isinstance(body["handoff"], bool)
    assert isinstance(body["restrictions"], list)
    assert isinstance(body["confidence"], (int, float))
    assert isinstance(body["matched_patterns"], list)
    assert isinstance(body["reason_codes"], list)