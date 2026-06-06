from __future__ import annotations

from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def elapsed_ms(start_perf: float, end_perf: float) -> float:
    return round((end_perf - start_perf) * 1000.0, 2)