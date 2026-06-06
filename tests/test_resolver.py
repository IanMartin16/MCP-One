from app.models.routing import OrchestrationInput
from app.routing.resolver import resolve_input


def test_resolve_crypto_market_summary():
    payload = OrchestrationInput(
        user_input="Give me a crypto market snapshot for BTC and ETH"
    )

    result = resolve_input(payload)

    assert result.intent_family == "market_summary"
    assert result.recommended_module == "cryptolink"
    assert "cryptolink" in result.selected_modules
    assert result.mode in {"summary", "composed_summary", "preview"}


def test_resolve_curp_validation():
    payload = OrchestrationInput(
        user_input="Help me validate a CURP in Mexico"
    )

    result = resolve_input(payload)

    assert result.intent_family == "identity_validation"
    assert result.recommended_module == "curpify"
    assert result.handoff is False


def test_resolve_secure_link_preview_or_handoff():
    payload = OrchestrationInput(
        user_input="I need fraud risk scoring for a transaction"
    )

    result = resolve_input(payload)

    assert result.intent_family == "risk_evaluation"
    assert result.recommended_module == "secure_link"
    assert result.handoff is True
    assert result.mode in {"handoff", "preview"}


def test_resolve_with_allowed_modules_filter_blocks_result():
    payload = OrchestrationInput(
        user_input="Help me validate a CURP in Mexico",
        allowed_modules=["cryptolink"],
    )

    result = resolve_input(payload)

    assert result.recommended_module is None
    assert result.handoff is True or result.mode in {"summary", "handoff"}
    assert len(result.selected_modules) == 0


def test_resolve_unknown_input_fallback():
    payload = OrchestrationInput(
        user_input="Tell me something completely unrelated to current registry"
    )

    result = resolve_input(payload)

    assert result.recommended_module is None
    assert result.intent_family is None
    assert result.confidence <= 0.2