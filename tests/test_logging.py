from app.utils.logging import get_logger


def test_get_logger():
    logger = get_logger()
    assert logger is not None
    assert logger.name == "mcp_one"