from time import monotonic

START_AT = monotonic()

def uptime_seconds() -> int:
    """Return the uptime of the application in seconds."""
    return int(monotonic() - START_AT)