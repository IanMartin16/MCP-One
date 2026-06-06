from app.models.routing import OrchestrationInput
from app.routing.resolver import resolve_input
from app.utils.reason_codes import ReasonCodes


def test_reason_codes_for_curpify_resolution():
    payload = OrchestrationInput(
        user_input="Help me validate a CURP in Mexico"
    )

    result = resolve_input(payload)

    assert ReasonCodes.RULE_MATCHED in result.reason_codes
    assert ReasonCodes.PRIMARY_MODULE_SELECTED in result.reason_codes
    assert ReasonCodes.SINGLE_MODULE_PATH in result.reason_codes
    assert ReasonCodes.ACTIVE_MODULE_SELECTED in result.reason_codes


def test_reason_codes_for_secure_link_handoff():
    payload = OrchestrationInput(
        user_input="I need fraud risk scoring for a transaction"
    )

    result = resolve_input(payload)

    assert ReasonCodes.RULE_MATCHED in result.reason_codes
    assert ReasonCodes.HANDOFF_REQUIRED in result.reason_codes
    assert (
        ReasonCodes.PLANNED_MODULE_SELECTED in result.reason_codes
        or ReasonCodes.BETA_MODULE_SELECTED in result.reason_codes
    )


def test_reason_codes_for_unknown_input():
    payload = OrchestrationInput(
        user_input="Completely unrelated request with no registry match"
    )

    result = resolve_input(payload)

    assert ReasonCodes.NO_RULE_MATCH in result.reason_codes
    assert ReasonCodes.FALLBACK_PATH in result.reason_codes