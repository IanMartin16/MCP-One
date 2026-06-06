from app.models.execution import ExecutionContext
from app.models.plan import OrchestrationPlan
from app.models.resolution import ResolutionResult
from app.orchestration.debug_mapper import build_debug_view


def test_build_debug_view_includes_execution_context():
    resolution = ResolutionResult(
        request_id="mcp-test-001",
        execution_context=ExecutionContext(
            request_id="mcp-test-001",
            client_context={
                "source": "nexus",
                "channel": "widget",
            },
            app_env="local",
            active_provider="none",
            enable_composition=True,
            enable_provider_enrichment=False,
            enable_structured_logging=True,
        ),
        intent_family="identity_validation",
        rule_id="rule_identity_validation_curpify",
        matched_patterns=["curp"],
        candidate_modules=["curpify"],
        candidate_capabilities=["identity.curp_validation"],
        selected_modules=["curpify"],
        selected_capabilities=["identity.curp_validation"],
        recommended_module="curpify",
        mode="summary",
        should_compose=False,
        handoff=False,
        restrictions=[],
        confidence=0.88,
        reason_codes=["RULE_MATCHED"],
        reasoning_notes=["Matched rule successfully."],
        plan=OrchestrationPlan(
            strategy="single_module",
            primary_module="curpify",
            primary_capability="identity.curp_validation",
        ),
    )

    debug = build_debug_view(resolution)

    assert debug.execution_context is not None
    assert debug.execution_context.request_id == "mcp-test-001"
    assert debug.execution_context.client_context["source"] == "nexus"