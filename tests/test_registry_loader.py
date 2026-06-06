from app.registry.loader import load_registry


def test_registry_loads_successfully():
    registry = load_registry()

    assert registry is not None
    assert len(registry.modules) > 0
    assert len(registry.capabilities) > 0
    assert len(registry.intent_rules) > 0