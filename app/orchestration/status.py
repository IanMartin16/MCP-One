from __future__ import annotations

from app.models.resolution import ResolutionResult
from app.utils.result_status import ResultStatus


def resolve_result_status(resolution: ResolutionResult) -> str:
    if not resolution.selected_modules:
        return ResultStatus.FALLBACK

    if resolution.handoff or resolution.mode == "handoff":
        return ResultStatus.HANDOFF_REQUIRED

    if resolution.mode == "preview":
        return ResultStatus.PREVIEW

    return ResultStatus.RESOLVED