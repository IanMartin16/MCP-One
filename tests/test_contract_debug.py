from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_orchestrate_debug_contract_shape():
    response = client.post(
        "/orchestrate/debug",
        json={
            "user_input": "Help me validate a CURP in Mexico",
            "request_id": "debug-contract-001",
            "client_context": {
                "source": "nexus",
                "channel": "widget",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert "result" in body
    assert "debug" in body

    result = body["result"]
    debug = body["debug"]

    assert "request_id" in result
    assert "status" in result
    assert "mode" in result
    assert "summary" in result

    assert "request_id" in debug
    assert "execution_context" in debug
    assert "intent_family" in debug
    assert "rule_id" in debug
    assert "reason_codes" in debug
    assert "reasoning_notes" in debug
    assert "plan" in debug