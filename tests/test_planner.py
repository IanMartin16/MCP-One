from app.models.resolution import ResolutionResult
from app.orchestration.planner import build_plan


def test_build_single_module_plan():
    resolution = ResolutionResult(
        selected_modules=["curpify"],
        selected_capabilities=["identity.curp_validation"],
        recommended_module="curpify",
        mode="summary",
        should_compose=False,
        handoff=False,
    )

    plan = build_plan(resolution)

    assert plan.strategy == "single_module"
    assert plan.primary_module == "curpify"
    assert len(plan.steps) == 1
    assert plan.steps[0].module_id == "curpify"


def test_build_handoff_plan():
    resolution = ResolutionResult(
        selected_modules=["secure_link"],
        selected_capabilities=["security.risk_evaluation_preview"],
        recommended_module="secure_link",
        mode="handoff",
        should_compose=False,
        handoff=True,
    )

    plan = build_plan(resolution)

    assert plan.strategy == "handoff"
    assert plan.requires_handoff is True
    assert len(plan.steps) == 1


def test_build_fallback_plan():
    resolution = ResolutionResult(
        selected_modules=[],
        selected_capabilities=[],
        recommended_module=None,
        mode="summary",
        should_compose=False,
        handoff=False,
    )

    plan = build_plan(resolution)

    assert plan.strategy == "fallback"
    assert plan.primary_module is None


def test_build_composed_plan():
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
    )

    plan = build_plan(resolution)

    assert plan.strategy == "composed"
    assert plan.primary_module == "cryptolink"
    assert len(plan.steps) == 2
    assert plan.steps[1].role == "secondary"