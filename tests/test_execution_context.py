from app.models.execution import ExecutionContext


def test_execution_context_creation():
    ctx = ExecutionContext(
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
    )

    assert ctx.request_id == "mcp-test-001"
    assert ctx.client_context["source"] == "nexus"
    assert ctx.active_provider == "none"
    assert ctx.enable_composition is True