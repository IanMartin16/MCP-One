from app.models.resolution import ResolutionResult
from app.orchestration.status import resolve_result_status
from app.utils.result_status import ResultStatus


def test_status_resolved():
    resolution = ResolutionResult(
        selected_modules=["curpify"],
        mode="summary",
        handoff=False,
    )
    assert resolve_result_status(resolution) == ResultStatus.RESOLVED


def test_status_handoff():
    resolution = ResolutionResult(
        selected_modules=["secure_link"],
        mode="handoff",
        handoff=True,
    )
    assert resolve_result_status(resolution) == ResultStatus.HANDOFF_REQUIRED


def test_status_fallback():
    resolution = ResolutionResult(
        selected_modules=[],
        mode="summary",
        handoff=False,
    )
    assert resolve_result_status(resolution) == ResultStatus.FALLBACK


def test_status_preview():
    resolution = ResolutionResult(
        selected_modules=["vision_link"],
        mode="preview",
        handoff=False,
    )
    assert resolve_result_status(resolution) == ResultStatus.PREVIEW