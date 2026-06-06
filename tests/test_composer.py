from app.models.resolution import ResolutionResult
from app.orchestration.composer import compose_output


def test_compose_single_module_output():
    resolution = ResolutionResult(
        intent_family="identity_validation",
        rule_id="rule_identity_validation_curpify",
        selected_modules=["curpify"],
        selected_capabilities=["identity.curp_validation"],
        recommended_module="curpify",
        mode="summary",
        should_compose=False,
        handoff=False,
        confidence=0.84,
    )

    output = compose_output(resolution)

    assert output.mode == "summary"
    assert output.recommended_module == "curpify"
    assert output.handoff is False
    assert "Curpify" in output.summary


def test_compose_handoff_output():
    resolution = ResolutionResult(
        intent_family="risk_evaluation",
        rule_id="rule_risk_eval_secure_preview",
        selected_modules=["secure_link"],
        selected_capabilities=["security.risk_evaluation_preview"],
        recommended_module="secure_link",
        mode="handoff",
        should_compose=False,
        handoff=True,
        confidence=0.77,
    )

    output = compose_output(resolution)

    assert output.mode == "handoff"
    assert output.handoff is True
    assert output.next_step is not None
    assert output.next_step.type == "handoff"


def test_compose_composed_summary_output():
    resolution = ResolutionResult(
        intent_family="trend_analysis",
        rule_id="rule_trend_analysis_composed",
        selected_modules=["cryptolink", "social_link"],
        selected_capabilities=[
            "crypto.market_trend_summary",
            "social.topic_attention",
        ],
        recommended_module="cryptolink",
        mode="composed_summary",
        should_compose=True,
        handoff=False,
        confidence=0.81,
    )

    output = compose_output(resolution)

    assert output.mode == "composed_summary"
    assert len(output.modules_used) == 2
    assert "CryptoLink" in output.summary or "Social Link" in output.summary