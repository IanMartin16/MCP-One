from __future__ import annotations

from typing import Any

# Campos de sobre: metadata común, no son la carga.
ENVELOPE_KEYS = {"ok", "fiat", "ts", "source", "provider", "summary"}


def normalize_data(raw: dict, kind: str | None = None) -> dict:
    if kind == "prices":
        return _normalize_prices(raw)

    if kind == "price_spark":
        return _normalize_price_spark(raw)    
        
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

def _normalize_prices(resp: dict) -> dict:
    prices = resp.get("prices") or {}
    change24h = resp.get("change24h") or {}
    market_cap = resp.get("marketCap") or {}

    rows = []
    for symbol, price in prices.items():
        row = {"symbol": symbol, "price": price}
        if symbol in change24h and change24h[symbol] is not None:
            row["change24h"] = change24h[symbol]
        if symbol in market_cap and market_cap[symbol] is not None:
            row["marketCap"] = market_cap[symbol]
        rows.append(row)

    return {"rows": rows}

def _normalize_price_spark(resp: dict) -> dict:
    series = resp.get("series") or {}

    rows = []

    if not isinstance(series, dict):
        return {"rows": rows}

    for symbol, raw_points in series.items():
        if not isinstance(raw_points, list):
            continue

        points = []

        for point in raw_points:
            if not isinstance(point, dict):
                continue

            ts = point.get("t")
            value = point.get("v")

            if value is None:
                continue

            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                continue

            points.append({
                "t": str(ts) if ts is not None else None,
                "v": numeric_value,
            })

        if len(points) < 2:
            continue

        rows.append({
            "symbol": str(symbol).upper(),
            "last": points[-1]["v"],
            "points": points,
        })

    return {"rows": rows}    