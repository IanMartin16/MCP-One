from __future__ import annotations

from collections import Counter, defaultdict
from threading import Lock


class MetricsStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._status_counter = Counter()
        self._mode_counter = Counter()
        self._plan_strategy_counter = Counter()
        self._recommended_module_counter = Counter()
        self._intent_family_counter = Counter()
        self._rule_id_counter = Counter()
        self._total_resolutions = 0

        self._duration_total_ms = 0.0
        self._duration_count = 0
        self._duration_min_ms: float | None = None
        self._duration_max_ms: float | None = None

        self._duration_by_status_total = defaultdict(float)
        self._duration_by_status_count = Counter()

        self._duration_by_mode_total = defaultdict(float)
        self._duration_by_mode_count = Counter()

        self._provider_attempts = 0
        self._provider_successes = 0
        self._provider_failures = 0
        self._provider_by_name = Counter()
        self._provider_by_model = Counter()

    def record(
        self,
        *,
        status: str | None,
        mode: str | None,
        plan_strategy: str | None,
        recommended_module: str | None,
        intent_family: str | None,
        rule_id: str | None,
        duration_ms: float | None = None,
    ) -> None:
        with self._lock:
            self._total_resolutions += 1

            if status:
                self._status_counter[status] += 1

            if mode:
                self._mode_counter[mode] += 1

            if plan_strategy:
                self._plan_strategy_counter[plan_strategy] += 1

            if recommended_module:
                self._recommended_module_counter[recommended_module] += 1

            if intent_family:
                self._intent_family_counter[intent_family] += 1

            if rule_id:
                self._rule_id_counter[rule_id] += 1

            if duration_ms is not None:
                self._duration_total_ms += duration_ms
                self._duration_count += 1

                if self._duration_min_ms is None or duration_ms < self._duration_min_ms:
                    self._duration_min_ms = duration_ms

                if self._duration_max_ms is None or duration_ms > self._duration_max_ms:
                    self._duration_max_ms = duration_ms

                if status:
                    self._duration_by_status_total[status] += duration_ms
                    self._duration_by_status_count[status] += 1

                if mode:
                    self._duration_by_mode_total[mode] += duration_ms
                    self._duration_by_mode_count[mode] += 1

    def record_provider_usage(
        self,
        *,
        provider: str | None,
        model: str | None,
        success: bool,
    ) -> None:
        with self._lock:
            self._provider_attempts += 1

            if success:
                self._provider_successes += 1
            else:
                self._provider_failures += 1

            if provider:
                self._provider_by_name[provider] += 1

            if model:
                self._provider_by_model[model] += 1

    def _safe_avg(self, total: float, count: int) -> float | None:
        if count == 0:
            return None
        return round(total / count, 2)

    def _avg_map(
        self,
        totals: dict[str, float],
        counts: Counter,
    ) -> dict[str, float]:
        result: dict[str, float] = {}
        for key, total in totals.items():
            count = counts.get(key, 0)
            avg = self._safe_avg(total, count)
            if avg is not None:
                result[key] = avg
        return result

    def _top_items(self, counter: Counter, limit: int) -> list[dict]:
        return [
            {"key": key, "count": count}
            for key, count in counter.most_common(limit)
        ]

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "total_resolutions": self._total_resolutions,
                "by_status": dict(self._status_counter),
                "by_mode": dict(self._mode_counter),
                "by_plan_strategy": dict(self._plan_strategy_counter),
                "by_recommended_module": dict(self._recommended_module_counter),
                "by_intent_family": dict(self._intent_family_counter),
                "by_rule_id": dict(self._rule_id_counter),
                "duration": {
                    "count": self._duration_count,
                    "avg_ms": self._safe_avg(self._duration_total_ms, self._duration_count),
                    "min_ms": self._duration_min_ms,
                    "max_ms": self._duration_max_ms,
                    "avg_by_status": self._avg_map(
                        self._duration_by_status_total,
                        self._duration_by_status_count,
                    ),
                    "avg_by_mode": self._avg_map(
                        self._duration_by_mode_total,
                        self._duration_by_mode_count,
                    ),
                },
                "provider_usage": {
                    "attempts": self._provider_attempts,
                    "successes": self._provider_successes,
                    "failures": self._provider_failures,
                    "by_provider": dict(self._provider_by_name),
                    "by_model": dict(self._provider_by_model),
                },
            }

    def summary(self, limit: int = 5) -> dict:
        with self._lock:
            return {
                "total_resolutions": self._total_resolutions,
                "duration": {
                    "count": self._duration_count,
                    "avg_ms": self._safe_avg(self._duration_total_ms, self._duration_count),
                    "min_ms": self._duration_min_ms,
                    "max_ms": self._duration_max_ms,
                },
                "provider_usage": {
                    "attempts": self._provider_attempts,
                    "successes": self._provider_successes,
                    "failures": self._provider_failures,
                    "top_providers": self._top_items(self._provider_by_name, limit),
                    "top_models": self._top_items(self._provider_by_model, limit),
                },
                "top_statuses": self._top_items(self._status_counter, limit),
                "top_modes": self._top_items(self._mode_counter, limit),
                "top_plan_strategies": self._top_items(self._plan_strategy_counter, limit),
                "top_recommended_modules": self._top_items(self._recommended_module_counter, limit),
                "top_intent_families": self._top_items(self._intent_family_counter, limit),
                "top_rule_ids": self._top_items(self._rule_id_counter, limit),
            }

    def reset(self) -> None:
        with self._lock:
            self._status_counter.clear()
            self._mode_counter.clear()
            self._plan_strategy_counter.clear()
            self._recommended_module_counter.clear()
            self._intent_family_counter.clear()
            self._rule_id_counter.clear()
            self._total_resolutions = 0

            self._duration_total_ms = 0.0
            self._duration_count = 0
            self._duration_min_ms = None
            self._duration_max_ms = None

            self._duration_by_status_total.clear()
            self._duration_by_status_count.clear()
            self._duration_by_mode_total.clear()
            self._duration_by_mode_count.clear()

            self._provider_attempts = 0
            self._provider_successes = 0
            self._provider_failures = 0
            self._provider_by_name.clear()
            self._provider_by_model.clear()


metrics_store = MetricsStore()