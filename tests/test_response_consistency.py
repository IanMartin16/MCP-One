from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _post_orchestrate(user_input: str, request_id: str) -> dict:
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
    return response.json()


def test_resolved_response_consistency():
    body = _post_orchestrate(
        user_input="Help me validate a CURP in Mexico",
        request_id="consistency-resolved-001",
    )

    assert body["status"] == "resolved"
    assert body["handoff"] is False
    assert body["mode"] in {"summary", "composed_summary", "module_recommendation", "capability_explanation"}

    next_step = body.get("next_step")
    assert next_step is not None
    assert next_step["type"] == "execute"

    assert body["recommended_module"] is not None


def test_fallback_response_consistency():
    body = _post_orchestrate(
        user_input="I need help with something unusual that doesn't map well",
        request_id="consistency-fallback-001",
    )

    assert body["status"] == "fallback"
    assert body["handoff"] is False

    next_step = body.get("next_step")
    assert next_step is not None
    assert next_step["type"] == "review"

    assert body["recommended_module"] is None


def test_handoff_response_consistency():
    body = _post_orchestrate(
        user_input="I need fraud risk scoring for a transaction",
        request_id="consistency-handoff-001",
    )

    assert body["status"] == "handoff_required"
    assert body["handoff"] is True
    assert body["mode"] == "handoff"

    next_step = body.get("next_step")
    assert next_step is not None
    assert next_step["type"] == "handoff"

    assert body["recommended_module"] is not None


def test_preview_response_consistency():
    body = _post_orchestrate(
        user_input="Can you analyze this image workflow for me?",
        request_id="consistency-preview-001",
    )

    assert body["status"] == "preview"
    assert body["handoff"] is False
    assert body["mode"] == "preview"

    next_step = body.get("next_step")
    assert next_step is not None
    assert next_step["type"] == "preview"

    assert body["recommended_module"] is not None