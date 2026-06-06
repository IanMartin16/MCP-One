from fastapi import APIRouter

from app.api.guards import require_debug_routes_enabled
from app.models.debug import OrchestrationDebugOutput
from app.models.routing import OrchestrationInput
from app.orchestration.composer import compose_output
from app.orchestration.debug_mapper import build_debug_view
from app.routing.resolver import resolve_input

router = APIRouter(tags=["orchestration"])


@router.post("/orchestrate")
def orchestrate(payload: OrchestrationInput):
    resolution = resolve_input(payload)
    return compose_output(resolution)


@router.post("/orchestrate/debug", response_model=OrchestrationDebugOutput)
def orchestrate_debug(payload: OrchestrationInput):
    disabled = require_debug_routes_enabled()
    if disabled is not None:
        return disabled

    resolution = resolve_input(payload)
    result = compose_output(resolution)
    debug = build_debug_view(resolution)

    return OrchestrationDebugOutput(
        result=result,
        debug=debug,
    )