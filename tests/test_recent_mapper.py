from app.models.execution import ExecutionContext
from app.models.plan import OrchestrationPlan
from app.models.resolution import ResolutionResult
from app.orchestration.recent_mapper import build_recent_resolution_item


def test_build_recent_resolution_item():
    resolution = ResolutionResult(
        request_id="mcp-test-001",
        client_context={
            "source": "nexus",
            "channel": "widget",
        },
        execution_context=ExecutionContext(
            request_id="mcp-test-001",
            client_context={
                "source": "nexus",
                "channel": "widget",
            },
            started_at="2026-03-31T00:00:00+00:00",
            duration_ms=5.5,
        ),
        status="resolved",
        intent_family="identity_validation",
        rule_id="rule_identity_validation_curpify",
        recommended_module="curpify",
        mode="summary",
        handoff=False,
        confidence=0.5,
        matched_patterns=["curp"],
        reason_codes=["RULE_MATCHED"],
        selected_modules=["curpify"],
        selected_capabilities=["identity.curp_validation"],
        plan=OrchestrationPlan(
            strategy="single_module",
            primary_module="curpify",
            primary_capability="identity.curp_validation",
        ),
    )

    item = build_recent_resolution_item(resolution)

    assert item["request_id"] == "mcp-test-001"
    assert item["status"] == "resolved"
    assert item["recommended_module"] == "curpify"
    assert item["plan_strategy"] == "single_module"
    assert item["duration_ms"] == 5.5