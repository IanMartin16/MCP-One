from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.execution.executor import (
    CryptoLinkExecutor,
    ExecutionRequest,
    ToolResult,
)
from app.models.registry import CapabilityDef

# Capability de lectura general cuando la desambiguación empata.
GENERAL_FALLBACK_CAPABILITY_ID = "crypto.exec.snapshot"


@dataclass
class RouterOutcome:
    """Subconjunto del resultado del router que el enganche necesita.

    El router YA resolvió qué capability ejecutar (selected_capabilities), así que
    el enganche la usa directo en vez de re-buscarla por intent_family. Eso elimina
    el desajuste entre el intent_family de las reglas y el de las capabilities.
    """

    module: str | None
    intent_family: str | None
    message: str | None
    selected_capabilities: list[str] | None = None  # del resolver (fuente de verdad)


class ExecutionBinding:
    def __init__(
        self,
        executor: CryptoLinkExecutor,
        execution_capabilities: Iterable[CapabilityDef],
    ):
        self._executor = executor
        # Índice por capability_id — el router ya nos dice cuál ejecutar.
        self._by_id = {
            c.capability_id: c
            for c in execution_capabilities
            if "tool_execution" in (c.output_modes or [])
        }
        # Se conserva la lista para el fallback por intent_family (compat).
        self._caps = list(self._by_id.values())

    async def resolve_and_execute(self, outcome: RouterOutcome) -> ToolResult | None:
        """
        Devuelve el toolResult neutral, o None si la intención no es de ejecución
        de Cryptolink (en cuyo caso MCPOne sigue su flujo de recomendación normal).
        """
        cap = self._select_capability(outcome)
        if cap is None:
            return None
        return await self._executor.execute(
            ExecutionRequest(capability=cap, message=outcome.message)
        )

    # ---- selección ---------------------------------------------------------

    def _select_capability(self, outcome: RouterOutcome) -> CapabilityDef | None:
        # 1) Vía principal: el router ya resolvió la capability. Úsala directo.
        for cap_id in (outcome.selected_capabilities or []):
            cap = self._by_id.get(cap_id)
            if cap is not None:
                return cap

        # 2) Fallback (compat): si no vino selected_capabilities, desambigua por
        #    intent_family + hints, como antes.
        candidates = self._candidates_for(outcome)
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]
        hinted = self._disambiguate(candidates, outcome.message)
        if hinted is not None:
            return hinted
        return self._general_fallback(candidates)

    def _candidates_for(self, outcome: RouterOutcome) -> list[CapabilityDef]:
        """Capabilities de ejecución que comparten módulo + intent_family."""
        module = (outcome.module or "").lower()
        fam = outcome.intent_family
        out = []
        for c in self._caps:
            if c.module_id.lower() != module:
                continue
            if fam and fam in (c.intent_families or []):
                out.append(c)
        return out

    @staticmethod
    def _disambiguate(
        candidates: list[CapabilityDef], message: str | None
    ) -> CapabilityDef | None:
        """Elige por `disambiguation_hints` declarados en la capability.

        Refinamiento acotado dentro de una intención ya resuelta — no es el
        `wantsX` del monolito viejo. Sin match claro -> None (cae al fallback).
        """
        if not message:
            return None
        msg = message.lower()
        best: CapabilityDef | None = None
        best_score = 0
        for c in candidates:
            hints = getattr(c, "disambiguation_hints", None) or []
            score = sum(1 for h in hints if h.lower() in msg)
            if score > best_score:
                best, best_score = c, score
        return best if best_score > 0 else None

    def _general_fallback(self, candidates: list[CapabilityDef]) -> CapabilityDef | None:
        """Snapshot como lectura general. Si no está disponible, no inventa: None."""
        for c in self._caps:
            if c.capability_id == GENERAL_FALLBACK_CAPABILITY_ID:
                return c
        # Sin snapshot declarado, mejor no adivinar entre las candidatas.
        return None
