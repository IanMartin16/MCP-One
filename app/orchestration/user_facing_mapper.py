from __future__ import annotations

from typing import Any

from app.models.resolution import ResolutionResult
from app.registry.access import get_capability


USER_FACING_PRODUCT_COPY = {
    "curpify": {
        "title": "Curpify",
        "summary": "Te ayuda a validar CURP y RFC con dígito verificador en México.",
        "context": "Útil para flujos de identidad y validación fiscal estructurada.",
        "next_step": "Si quieres, te explico cómo obtener tu API key o cómo integrarlo en tu código.",
        "offer_help": "Puedo ayudarte con integración, ejemplos de uso o troubleshooting.",
    },
        "evilink_overview": {
        "title": "Evilink",
        "summary": "Es un ecosistema de APIs, productos y capas de integración orientado a validación, datos estructurados, observabilidad, secretos y rutas especializadas.",
        "context": "Incluye productos como Curpify, Data_Link, V-Secrets, Status-Hub y CryptoLink, cada uno enfocado en necesidades distintas dentro del ecosistema.",
        "next_step": "Si quieres, te explico qué hace cada producto o cuál encaja mejor con tu caso.",
        "offer_help": "Puedo ayudarte a ubicar el producto correcto según tu necesidad.",
    },
    "datalink": {
        "title": "Data_Link",
        "summary": "Sirve para limpiar, deduplicar, filtrar y transformar archivos como CSV o JSON.",
        "context": "Útil cuando necesitas preparar datos antes de cargarlos a otro sistema.",
        "next_step": "Si quieres, te explico qué tipo de limpieza puedes hacer sobre CSV o JSON.",
        "offer_help": "Puedo ayudarte a entender si te conviene para deduplicar, filtrar o transformar datos.",
    },
    "v_secrets": {
        "title": "V-Secrets",
        "summary": "Sirve para gestionar secretos, API keys y configuraciones sensibles de forma segura.",
        "context": "Útil cuando necesitas proteger credenciales, tokens o material sensible.",
        "next_step": "Si quieres, te explico en qué casos usarlo para secretos, llaves o credenciales.",
        "offer_help": "Puedo ayudarte con contexto de uso, integración o mejores prácticas básicas.",
    },
    "status_hub": {
        "title": "Status-Hub",
        "summary": "Te ayuda a revisar el estado y salud operativa de apps y servicios del ecosistema.",
        "context": "Útil para verificar si una app está activa, degradada o con incidentes.",
        "next_step": "Si quieres, te explico qué tipo de health o estado operativo puedes revisar desde ahí.",
        "offer_help": "Puedo ayudarte a entender cuándo usarlo para monitoreo o diagnóstico rápido.",
    },
    "secure_link": {
        "title": "Secure Link",
        "summary": "Se orienta a evaluación de riesgo y seguridad, con acceso más controlado.",
        "context": "Útil para casos de riesgo, fraude o decisiones sensibles.",
        "next_step": "Si quieres, te explico en qué escenarios encaja mejor dentro del ecosistema.",
        "offer_help": "Puedo ayudarte a ubicar si tu caso cae en riesgo, fraude o decisión sensible.",
    },
}

FALLBACK_COPY = {
    "title": "Alcance actual",
    "summary": "No encontré una coincidencia clara dentro del ecosistema actual.",
    "context": "Hoy Evilink se enfoca en validación, datos estructurados, observabilidad, secretos y rutas especializadas.",
    "next_step": "Prueba describiendo si necesitas validación, limpieza de datos, observabilidad o gestión de secretos.",
}


def _resolve_capability_name(result: ResolutionResult) -> str | None:
    if not result.selected_capabilities:
        return None

    capability = get_capability(result.selected_capabilities[0])
    if capability and capability.name:
        return capability.name

    return result.selected_capabilities[0]


def _resolve_discovery_mode(result: ResolutionResult) -> str:
    if result.handoff or result.mode == "handoff":
        return "specialized_route"

    if result.recommended_module and result.status == "resolved":
        return "exact_fit"

    if result.status == "fallback":
        return "generic"

    return "generic"


def build_user_facing_payload(result: ResolutionResult) -> dict[str, Any]:
    capability_name = _resolve_capability_name(result)
    discovery_mode = _resolve_discovery_mode(result)

    if result.recommended_module and result.status == "resolved":
        product_copy = USER_FACING_PRODUCT_COPY.get(result.recommended_module)

        if product_copy:
            return {
                "product_name": product_copy["title"],
                "capability_name": capability_name,
                "discovery_mode": discovery_mode,
                "user_facing_title": product_copy["title"],
                "user_facing_summary": product_copy["summary"],
                "user_facing_context": product_copy["context"],
                "next_step_hint": product_copy["next_step"],
                "offer_help": product_copy["offer_help"],
            }

    return {
        "product_name": None,
        "capability_name": capability_name,
        "discovery_mode": discovery_mode,
        "user_facing_title": "Alcance actual",
        "user_facing_summary": "No encontré una coincidencia clara dentro del ecosistema actual.",
        "user_facing_context": "Hoy Evilink se enfoca en validación, datos estructurados, observabilidad, secretos y rutas especializadas.",
        "next_step_hint": "Prueba describiendo si necesitas validación, limpieza de datos, observabilidad o gestión de secretos.",
        "offer_help": "Puedo ayudarte a reformular tu necesidad para ubicar la ruta más cercana dentro del ecosistema.",
    }