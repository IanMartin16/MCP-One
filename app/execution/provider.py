from __future__ import annotations

from functools import lru_cache

from app.execution.binding import ExecutionBinding
from app.execution.executor import CryptoLinkExecutor
from app.utils.cryptolink_client import CryptoLinkClient

# Importa la lista de capabilities de ejecución. Ajustar al lugar donde las
# declares (junto al REGISTRY en data.py, o un módulo dedicado).
from app.registry.cryptolink_execution_capabilities import (
    CRYPTOLINK_EXECUTION_CAPABILITIES,
)


@lru_cache
def get_execution_binding() -> ExecutionBinding:
    client = CryptoLinkClient()                       # AsyncClient perezoso
    executor = CryptoLinkExecutor(client)
    return ExecutionBinding(executor, CRYPTOLINK_EXECUTION_CAPABILITIES)
