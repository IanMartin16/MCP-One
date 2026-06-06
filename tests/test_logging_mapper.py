from app.models.plan import OrchestrationPlan
from app.models.resolution import ResolutionResult
from app.orchestration.logging_mapper import build_resolution_log_payload


def test_build_resolution_log_payload_includes_client_context():
    resolution = ResolutionResult(
        request_id="mcp-test-001",
        client_context={
            "source": "nexus",
            "channel": "widget",
            "session_id": "sess-123",
        },
        intent_family="identity_validation",
        rule_id="rule_identity_validation_curpify",
        selected_modules=["curpify"],
        selected_capabilities=["identity.curp_validation"],
        recommended_module="curpify",
        mode="summary",
        handoff=False,
        confidence=0.88,
        matched_patterns=["curp"],
        reason_codes=["RULE_MATCHED"],
        plan=OrchestrationPlan(
            strategy="single_module",
            primary_module="curpify",
            primary_capability="identity.curp_validation",
        ),
    )

    payload = build_resolution_log_payload(resolution)

    assert payload["client_context"]["source"] == "nexus"
    assert payload["client_context"]["channel"] == "widget"
    assert payload["client_context"]["session_id"] == "sess-123"