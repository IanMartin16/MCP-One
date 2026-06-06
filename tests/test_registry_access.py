from app.registry.access import (
    get_all_modules,
    get_all_capabilities,
    get_all_rules,
    get_module,
    get_capability,
    find_rules_by_intent_family,
)


def test_get_all_modules():
    modules = get_all_modules()
    assert len(modules) > 0


def test_get_all_capabilities():
    capabilities = get_all_capabilities()
    assert len(capabilities) > 0


def test_get_all_rules():
    rules = get_all_rules()
    assert len(rules) > 0


def test_get_module_by_id():
    module = get_module("cryptolink")
    assert module is not None
    assert module.module_id == "cryptolink"


def test_get_capability_by_id():
    capability = get_capability("crypto.price_lookup")
    assert capability is not None
    assert capability.capability_id == "crypto.price_lookup"


def test_find_rules_by_intent_family():
    rules = find_rules_by_intent_family("market_summary")
    assert len(rules) > 0
    assert rules[0].intent_family == "market_summary"