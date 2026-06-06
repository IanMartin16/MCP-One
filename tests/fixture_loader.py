from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "nexus_mcp_one"


def load_fixture(name: str) -> dict[str, Any]:
    path = FIXTURES_DIR / name
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)