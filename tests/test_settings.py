from app.config.settings import get_settings


def test_settings_load():
    settings = get_settings()

    assert settings.app_name == "MCP-One"
    assert settings.app_version is not None
    assert settings.default_confidence_floor >= 0.0
    assert settings.default_confidence_cap <= 1.0