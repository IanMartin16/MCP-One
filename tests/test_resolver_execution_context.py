from app.models.routing import OrchestrationInput
from app.routing.resolver import resolve_input


def test_resolve_input_builds_execution_context():
    payload = OrchestrationInput(
        user_input="Help me validate a CURP in Mexico",
        client_context={
            "source": "nexus",
            "channel": "widget",
            "session_id": "sess-001",
            "tenant": "evilink-dev",
        },
    )

    result = resolve_input(payload)

    assert result.execution_context is not None
    assert result.execution_context.request_id is not None
    assert result.execution_context.client_context["source"] == "nexus"
    assert result.execution_context.client_context["channel"] == "widget"
    assert result.execution_context.started_at is not None
    assert result.execution_context.duration_ms is not None
    assert result.execution_context.duration_ms >= 0