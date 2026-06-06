from app.utils.trace import generate_request_id


def test_generate_request_id():
    request_id = generate_request_id()

    assert request_id.startswith("mcp-")
    assert len(request_id) > 8
    