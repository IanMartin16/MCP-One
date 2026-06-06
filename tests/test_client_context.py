from app.utils.client_context import sanitize_client_context


def test_sanitize_client_context_allows_only_whitelisted_keys():
    raw = {
        "source": "nexus",
        "channel": "widget",
        "tenant": "evilink",
        "session_id": "sess-123",
        "user_role": "developer",
        "foo": "bar",
        "secret": "nope",
    }

    sanitized = sanitize_client_context(raw)

    assert sanitized == {
        "source": "nexus",
        "channel": "widget",
        "tenant": "evilink",
        "session_id": "sess-123",
        "user_role": "developer",
    }


def test_sanitize_client_context_ignores_none_values():
    raw = {
        "source": "nexus",
        "channel": None,
        "session_id": "sess-123",
    }

    sanitized = sanitize_client_context(raw)

    assert sanitized == {
        "source": "nexus",
        "session_id": "sess-123",
    }


def test_sanitize_client_context_stringifies_non_scalar_values():
    raw = {
        "source": "nexus",
        "session_id": ["a", "b"],
    }

    sanitized = sanitize_client_context(raw)

    assert sanitized["source"] == "nexus"
    assert sanitized["session_id"] == "['a', 'b']"