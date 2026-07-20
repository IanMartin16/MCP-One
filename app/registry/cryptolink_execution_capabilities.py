"""
cryptolink_execution_capabilities.py — capabilities de EJECUCIÓN de Cryptolink.
                                        (módulo independiente, en MCPOne)

Ruta sugerida: app/registry/cryptolink_execution_capabilities.py
El provider lo importa:
    from app.registry.cryptolink_execution_capabilities import (
        CRYPTOLINK_EXECUTION_CAPABILITIES,
    )

Cada capability es autodescriptiva: output_modes=["tool_execution"],
execution_endpoint (método del cliente) y output_kind (kind neutral).

`disambiguation_hints`: pistas que usa el ENGANCHE cuando varias capabilities
comparten intent_family, para elegir la correcta. NO es detección de intención
(eso ya lo hizo el router); es refinamiento dentro de una intención ya resuelta.

Familias con ambigüedad (por eso llevan hints):
  - trend_analysis  -> momentum vs trends
  - market_summary  -> varias caen aquí
Si ninguna pista gana, el enganche cae a snapshot (lectura general honesta).
"""

from app.models.registry import CapabilityDef

CRYPTOLINK_EXECUTION_CAPABILITIES = [
    CapabilityDef(
        capability_id="crypto.exec.prices",
        module_id="cryptolink",
        name="Price Lookup (exec)",
        description="Executes a live price lookup for crypto assets.",
        exposure="public",
        tags=["price", "quote", "execution"],
        intent_families=["asset_lookup", "market_lookup"],
        output_modes=["tool_execution"],
        execution_endpoint="get_prices",
        output_kind="prices",
        disambiguation_hints=["precio", "price", "cotiza", "vale", "valor", "cuánto", "cuanto"],
    ),
    CapabilityDef(
        capability_id="crypto.exec.movers",
        module_id="cryptolink",
        name="Top Movers (exec)",
        description="Executes top movers (gainers/losers) retrieval.",
        exposure="public",
        tags=["movers", "gainers", "losers", "execution"],
        intent_families=["market_movers", "market_summary"],
        output_modes=["tool_execution"],
        execution_endpoint="get_movers",
        output_kind="movers",
        disambiguation_hints=["movers", "top movers", "gainers", "losers", "subio", "subió", "bajo", "bajó"],
    ),
    CapabilityDef(
        capability_id="crypto.exec.momentum",
        module_id="cryptolink",
        name="Momentum (exec)",
        description="Executes momentum signal retrieval for assets.",
        exposure="public",
        tags=["momentum", "strength", "execution"],
        intent_families=["trend_analysis", "market_summary"],
        output_modes=["tool_execution"],
        execution_endpoint="get_momentum",
        output_kind="momentum",
        disambiguation_hints=["momentum", "fuerza", "strength", "traccion", "tracción", "consistencia"],
    ),
    CapabilityDef(
        capability_id="crypto.exec.regime",
        module_id="cryptolink",
        name="Market Regime (exec)",
        description="Executes market regime interpretation retrieval.",
        exposure="public",
        tags=["regime", "market", "execution"],
        intent_families=["market_regime", "trend_analysis"],
        output_modes=["tool_execution"],
        execution_endpoint="get_regime",
        output_kind="regime",
        disambiguation_hints=["regime", "regimen", "régimen", "sesgo", "estado del mercado"],
    ),
    CapabilityDef(
        capability_id="crypto.exec.trends",
        module_id="cryptolink",
        name="Market Trends (exec)",
        description="Executes trend signal retrieval for assets.",
        exposure="public",
        tags=["trend", "trends", "execution"],
        intent_families=["trend_analysis", "market_summary"],
        output_modes=["tool_execution"],
        execution_endpoint="get_trends",
        output_kind="trends",
        disambiguation_hints=["trend", "trends", "tendencia", "tendencias", "fuerte"],
    ),
    CapabilityDef(
        capability_id="crypto.exec.risk_flags",
        module_id="cryptolink",
        name="Risk Flags (exec)",
        description="Executes risk flag retrieval for assets.",
        exposure="public",
        tags=["risk", "flags", "execution"],
        intent_families=["risk_evaluation", "market_summary"],
        output_modes=["tool_execution"],
        execution_endpoint="get_risk_flags",
        output_kind="risk_flags",
        disambiguation_hints=["risk flags", "risk", "riesgo", "riesgos", "alertas", "banderas"],
    ),
    CapabilityDef(
        capability_id="crypto.exec.anomalies",
        module_id="cryptolink",
        name="Anomalies (exec)",
        description="Executes anomaly detection retrieval for assets.",
        exposure="public",
        tags=["anomalies", "outliers", "execution"],
        intent_families=["anomaly_detection", "market_summary"],
        output_modes=["tool_execution"],
        execution_endpoint="get_anomalies",
        output_kind="anomalies",
        disambiguation_hints=["anomalies", "anomaly", "anomalia", "anomalía", "outlier", "inusual", "raro"],
    ),
    CapabilityDef(
        capability_id="crypto.exec.market_health",
        module_id="cryptolink",
        name="Market Health (exec)",
        description="Executes market health summary retrieval.",
        exposure="public",
        tags=["health", "market", "execution"],
        intent_families=["market_health", "market_summary"],
        output_modes=["tool_execution"],
        execution_endpoint="get_market_health",
        output_kind="market_health",
        disambiguation_hints=["market health", "health", "salud del mercado", "salud"],
    ),
    CapabilityDef(
        capability_id="crypto.exec.social_pulse",
        module_id="cryptolink",
        name="Social Pulse (exec)",
        description="Executes social pulse / narrative retrieval.",
        exposure="public",
        tags=["social", "narrative", "execution"],
        intent_families=["sentiment_analysis", "topic_attention"],
        output_modes=["tool_execution"],
        execution_endpoint="get_social_pulse",
        output_kind="social_pulse",
        disambiguation_hints=["social pulse", "narrative", "narrativa", "sentiment", "sentimiento"],
    ),
    CapabilityDef(
        capability_id="crypto.exec.snapshot",
        module_id="cryptolink",
        name="Market Snapshot (exec)",
        description="Executes a market snapshot retrieval (no symbols required).",
        exposure="public",
        tags=["snapshot", "overview", "execution"],
        intent_families=["market_snapshot", "market_summary"],
        output_modes=["tool_execution"],
        execution_endpoint="get_snapshot",
        output_kind="snapshot",
        disambiguation_hints=["snapshot", "overview", "resumen", "mood", "panorama"],
    ),
    CapabilityDef(
        capability_id="crypto.exec.price_spark",
        module_id="cryptolink",
        name="Price Spark (exec)",
        description="Executes price sparkline (recent series) retrieval.",
        exposure="public",
        tags=["spark", "series", "execution"],
        intent_families=["asset_lookup", "trend_analysis"],
        output_modes=["tool_execution"],
        execution_endpoint="get_price_spark",
        output_kind="price_spark",
        disambiguation_hints=["spark", "sparkline", "serie", "series"],
    ),
]