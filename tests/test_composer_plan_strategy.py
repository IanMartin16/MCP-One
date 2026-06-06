from app.models.plan import OrchestrationPlan, PlanStep
from app.models.resolution import ResolutionResult
from app.orchestration.composer import compose_output


def test_compose_output_single_module_plan():
    resolution = ResolutionResult(
        selected_modules=["curpify"],
        selected_capabilities=["identity.curp_validation"],
        recommended_module="curpify",
        mode="summary",
        should_compose=False,
        handoff=False,
        confidence=0.82,
        matched_patterns=["curp"],
        reason_codes=["RULE_MATCHED"],
        plan=OrchestrationPlan(
            strategy="single_module",
            primary_module="curpify",
            primary_capability="identity.curp_validation",
            steps=[
                PlanStep(
                    step_id="step-1",
                    module_id="curpify",
                    capability_id="identity.curp_validation",
                    role="primary",
                    optional=False,
                    reason="Single-module execution path selected.",
                )
            ],
            requires_handoff=False,
            preview_only=False,
            notes=["Single-module orchestration plan generated."],
        ),
    )

    output = compose_output(resolution)

    assert output.mode == "summary"
    assert "Curpify" in output.summary
    assert "solo módulo" in output.insight or "single" not in output.insight.lower()


def test_compose_output_handoff_plan():
    resolution = ResolutionResult(
        selected_modules=["secure_link"],
        selected_capabilities=["security.risk_evaluation_preview"],
        recommended_module="secure_link",
        mode="handoff",
        should_compose=False,
        handoff=True,
        confidence=0.7,
        matched_patterns=["risk"],
        reason_codes=["HANDOFF_REQUIRED"],
        plan=OrchestrationPlan(
            strategy="handoff",
            primary_module="secure_link",
            primary_capability="security.risk_evaluation_preview",
            steps=[
                PlanStep(
                    step_id="step-1",
                    module_id="secure_link",
                    capability_id="security.risk_evaluation_preview",
                    role="primary",
                    optional=False,
                    reason="Primary module identified, but handoff is required.",
                )
            ],
            requires_handoff=True,
            preview_only=False,
            notes=["Resolution requires handoff before execution."],
        ),
    )

    output = compose_output(resolution)

    assert output.handoff is True
    assert "handoff" in output.summary.lower() or "handoff" in output.insight.lower()


def test_compose_output_composed_plan():
    resolution = ResolutionResult(
        selected_modules=["cryptolink", "social_link"],
        selected_capabilities=[
            "crypto.market_trend_summary",
            "social.sentiment_summary",
        ],
        recommended_module="cryptolink",
        mode="composed_summary",
        should_compose=True,
        handoff=False,
        confidence=0.87,
        matched_patterns=["trend", "sentiment"],
        reason_codes=["COMPOSITION_ENABLED"],
        plan=OrchestrationPlan(
            strategy="composed",
            primary_module="cryptolink",
            primary_capability="crypto.market_trend_summary",
            secondary_modules=["social_link"],
            secondary_capabilities=["social.sentiment_summary"],
            steps=[
                PlanStep(
                    step_id="step-1",
                    module_id="cryptolink",
                    capability_id="crypto.market_trend_summary",
                    role="primary",
                    optional=False,
                    reason="Primary module in composed flow.",
                ),
                PlanStep(
                    step_id="step-2",
                    module_id="social_link",
                    capability_id="social.sentiment_summary",
                    role="secondary",
                    optional=True,
                    reason="Secondary supporting module in composed flow.",
                ),
            ],
            requires_handoff=False,
            preview_only=False,
            notes=["Composed orchestration plan generated."],
        ),
    )

    output = compose_output(resolution)

    assert output.mode == "composed_summary"
    assert "compuesta" in output.summary.lower() or "compuesto" in output.summary.lower()