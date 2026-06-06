def assert_orchestration_output_contract(body: dict):
    required_fields = {
        "request_id",
        "status",
        "mode",
        "modules_used",
        "capabilities_used",
        "summary",
        "handoff",
        "restrictions",
        "confidence",
        "matched_patterns",
        "reason_codes",
    }

    assert required_fields.issubset(body.keys())

    assert isinstance(body["request_id"], (str, type(None)))
    assert isinstance(body["status"], (str, type(None)))
    assert isinstance(body["mode"], str)
    assert isinstance(body["modules_used"], list)
    assert isinstance(body["capabilities_used"], list)
    assert isinstance(body["summary"], str)
    assert isinstance(body["handoff"], bool)
    assert isinstance(body["restrictions"], list)
    assert isinstance(body["confidence"], (int, float))
    assert isinstance(body["matched_patterns"], list)
    assert isinstance(body["reason_codes"], list)


def assert_error_contract(body: dict):
    assert "error" in body
    error = body["error"]

    required_fields = {
        "code",
        "message",
        "request_id",
        "details",
    }
    assert required_fields.issubset(error.keys())

    assert isinstance(error["code"], str)
    assert isinstance(error["message"], str)
    assert isinstance(error["request_id"], (str, type(None)))
    assert isinstance(error["details"], dict)