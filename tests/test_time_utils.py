from app.utils.time import elapsed_ms, utc_now_iso


def test_utc_now_iso_returns_string():
    value = utc_now_iso()

    assert isinstance(value, str)
    assert "T" in value


def test_elapsed_ms_returns_positive_number():
    value = elapsed_ms(1.0, 1.25)

    assert value == 250.0