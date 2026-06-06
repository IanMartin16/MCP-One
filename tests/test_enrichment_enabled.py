import os

from app.config.settings import get_settings
from app.models.resolution import ResolutionResult
from app.orchestration.composer import compose_output


def test_compose_output_with_provider_enrichment(monkeypatch):
    monkeypatch.setenv("ENABLE_PROVIDER_ENRICHMENT", "true")
    monkeypatch.setenv("ACTIVE_PROVIDER", "openai")
    get_settings.cache_clear()

    resolution = ResolutionResult(
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
        confidence=0.88,
        reason_codes=[
            "RULE_MATCHED",
            "PRIMARY_MODULE_SELECTED",
            "SINGLE_MODULE_PATH",
            "ACTIVE_MODULE_SELECTED",
        ],
    )

    output = compose_output(resolution)

    assert output.summary is not None
    assert "Stub response from OpenAIClient" in output.summary

    get_settings.cache_clear()