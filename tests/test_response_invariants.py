from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


SCENARIOS = [
    ("Help me validate a CURP in Mexico", "inv-resolved-001"),
    ("I need fraud risk scoring for a transaction", "inv-handoff-001"),
    ("Can you analyze this image workflow for me?", "inv-preview-001"),
    ("I need help with something unusual that doesn't map well", "inv-fallback-001"),
]


def test_status_handoff_invariants():
    for user_input, request_id in SCENARIOS:
        response = client.post(
            "/orchestrate",
            json={
                "user_input": user_input,
                "request_id": request_id,
                "client_context": {
                    "source": "nexus",
                    "channel": "widget",
                },
            },
        )
        assert response.status_code == 200
        body = response.json()

        status = body["status"]
        mode = body["mode"]
        handoff = body["handoff"]
        next_step = body.get("next_step") or {}

        if status == "resolved":
            assert handoff is False
            assert mode != "handoff"
            assert next_step.get("type") == "execute"

        if status == "handoff_required":
            assert handoff is True
            assert mode == "handoff"
            assert next_step.get("type") == "handoff"

        if status == "fallback":
            assert handoff is False
            assert next_step.get("type") == "review"
            assert body["recommended_module"] is None

        if status == "preview":
            assert mode == "preview"
            assert next_step.get("type") == "preview"