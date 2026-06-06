from app.metrics.collector import record_resolution_metrics
from app.metrics.store import metrics_store
from app.models.execution import ExecutionContext
from app.models.plan import OrchestrationPlan
from app.models.resolution import ResolutionResult


def test_record_resolution_metrics_with_duration():
    metrics_store.reset()

    resolution = ResolutionResult(
        status="resolved",
        intent_family="identity_validation",
        rule_id="rule_identity_validation_curpify",
        mode="summary",
        recommended_module="curpify",
        execution_context=ExecutionContext(
            request_id="mcp-test-001",
            duration_ms=12.5,
        ),
        plan=OrchestrationPlan(
            strategy="single_module",
            primary_module="curpify",
            primary_capability="identity.curp_validation",
        ),
    )

    record_resolution_metrics(resolution)

    snapshot = metrics_store.snapshot()

    assert snapshot["duration"]["count"] == 1
    assert snapshot["duration"]["avg_ms"] == 12.5
    assert snapshot["duration"]["min_ms"] == 12.5
    assert snapshot["duration"]["max_ms"] == 12.5