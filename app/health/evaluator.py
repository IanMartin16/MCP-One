from __future__ import annotations

from dataclasses import dataclass

from app.registry.loader import load_registry


@dataclass(frozen=True)
class HealthEvaluation:
    registry_ready: bool

    @property
    def ready(self) -> bool:
        return self.registry_ready

    @property
    def operational_status(self) -> str:
        return "operational" if self.ready else "degraded"

    @property
    def readiness_status(self) -> str:
        return "ready" if self.ready else "not_ready"


def evaluate_health() -> HealthEvaluation:
    try:
        registry = load_registry()

        registry_ready = (
            bool(registry.modules)
            and bool(registry.capabilities)
            and bool(registry.intent_rules)
        )

        return HealthEvaluation(
            registry_ready=registry_ready,
        )
    except Exception:
        return HealthEvaluation(
            registry_ready=False,
        )