from app.models.errors import ErrorEnvelope, ErrorPayload


def test_error_models():
    envelope = ErrorEnvelope(
        error=ErrorPayload(
            code="VALIDATION_ERROR",
            message="The request payload failed validation.",
            request_id="req-001",
            details={"field": "user_input"},
        )
    )

    assert envelope.error.code == "VALIDATION_ERROR"
    assert envelope.error.request_id == "req-001"
    assert envelope.error.details["field"] == "user_input"