from app.models.resolution import ResolutionResult
from app.orchestration.composer import compose_output


def test_next_step_review_when_no_module():
    resolution = ResolutionResult(
        status="fallback",
        recommended_module=None,
        selected_modules=[],
        selected_capabilities=[],
        mode="summary",
        handoff=False,
        confidence=0.1,
        matched_patterns=[],
        reason_codes=["NO_RULE_MATCH"],
    )

    output = compose_output(resolution)
    assert output.next_step is not None
    assert output.next_step.type == "review"


def test_next_step_handoff_when_handoff_true():
    resolution = ResolutionResult(
        status="handoff_required",
        recommended_module="secure_link",
        selected_modules=["secure_link"],
        selected_capabilities=["security.risk_evaluation_preview"],
        mode="handoff",
        handoff=True,
        confidence=0.7,
        matched_patterns=["risk"],
        reason_codes=["HANDOFF_REQUIRED"],
    )

    output = compose_output(resolution)
    assert output.next_step is not None
    assert output.next_step.type == "handoff"


def test_next_step_preview_when_mode_preview():
    resolution = ResolutionResult(
        status="preview",
        recommended_module="vision_link",
        selected_modules=["vision_link"],
        selected_capabilities=["vision.image_analysis_preview"],
        mode="preview",
        handoff=False,
        confidence=0.6,
        matched_patterns=["image"],
        reason_codes=["PREVIEW_MODE"],
    )

    output = compose_output(resolution)
    assert output.next_step is not None
    assert output.next_step.type == "preview"


def test_next_step_execute_for_normal_resolved():
    resolution = ResolutionResult(
        status="resolved",
        recommended_module="curpify",
        selected_modules=["curpify"],
        selected_capabilities=["identity.curp_validation"],
        mode="summary",
        handoff=False,
        confidence=0.8,
        matched_patterns=["curp"],
        reason_codes=["RULE_MATCHED"],
    )

    output = compose_output(resolution)
    assert output.next_step is not None
    assert output.next_step.type == "execute"