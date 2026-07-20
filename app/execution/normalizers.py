"""
normalizers.py — normalización ESTRUCTURAL del data crudo.  (vive en MCPOne)

Ruta sugerida: app/execution/normalizers.py

Convierte el `data` crudo de CryptoLink a una forma uniforme para que nexus-slim
lo reciba predecible. Este archivo ES el contrato neutral (lado MCPOne): define
qué forma tiene cada kind al cruzar hacia nexus-slim. El contract.py de nexus-slim
es la misma frontera vista desde el otro lado.

PRINCIPIO CLAVE — no mira adentro del dato:
No conoce los campos internos (que momentum trae `strength`, que regime trae
`score`...). Solo reordena la FORMA. Por eso es robusto ante contratos crudos
inconsistentes: nunca los inspecciona.

Las respuestas crudas tienen la misma anatomía:
  - campos de SOBRE conocidos: ok, fiat, ts, source, summary
  - UNA llave de carga con el nombre del recurso (momentum, regime, flags...)
    que NO siempre coincide con el kind (risk_flags -> llave "flags").

Regla estructural:
  1) quita el sobre.
  2) lo que queda es la llave de carga (por descarte, sin asumir su nombre).
  3) si su valor es lista  -> data["rows"] = lista
     si es objeto          -> sube sus campos a data (plano)
  4) preserva `summary` del sobre si venía (risk_flags/anomalies lo traen).

Familias (solo para documentar; la regla es la misma para todas):
  lista-por-símbolo: momentum, trends, movers, risk_flags, anomalies -> rows
  agregada:          regime, market_health, snapshot, social_pulse   -> plano
"""

from __future__ import annotations

from typing import Any

# Campos de sobre: metadata común, no son la carga.
ENVELOPE_KEYS = {"ok", "fiat", "ts", "source", "provider", "summary"}


def normalize_data(raw: dict[str, Any]) -> dict[str, Any]:
    """Reubica la carga cruda a forma uniforme. No inspecciona contenido."""
    if not isinstance(raw, dict):
        return {"rows": []}

    # 1) preservar el summary del sobre si venía.
    out: dict[str, Any] = {}
    if "summary" in raw and raw.get("summary") is not None:
        out["summary"] = raw["summary"]

    # 2) encontrar la(s) llave(s) de carga por descarte (lo que no es sobre).
    payload_keys = [k for k in raw.keys() if k not in ENVELOPE_KEYS]

    # Caso normal: una sola llave de carga.
    if len(payload_keys) == 1:
        payload = raw[payload_keys[0]]
        return _reshape(payload, out)

    # Caso snapshot y similares: la carga puede venir anidada bajo su nombre,
    # o haber varias llaves. Si hay una llave cuyo valor es dict/list, se toma
    # como carga principal; el resto se conserva plano.
    if not payload_keys:
        return out  # solo sobre; nada que reubicar

    # Varias llaves: reubica la primera estructurada, conserva el resto plano.
    main_key = None
    for k in payload_keys:
        if isinstance(raw[k], (list, dict)):
            main_key = k
            break
    if main_key is None:
        # todas escalares -> súbelas planas
        for k in payload_keys:
            out[k] = raw[k]
        return out

    reshaped = _reshape(raw[main_key], out)
    for k in payload_keys:
        if k != main_key:
            reshaped.setdefault(k, raw[k])
    return reshaped


def _reshape(payload: Any, out: dict[str, Any]) -> dict[str, Any]:
    """lista -> rows ; objeto -> campos planos ; escalar -> value."""
    if isinstance(payload, list):
        out["rows"] = payload
    elif isinstance(payload, dict):
        out.update(payload)  # sube los campos del objeto a plano
    else:
        out["value"] = payload
    return out
