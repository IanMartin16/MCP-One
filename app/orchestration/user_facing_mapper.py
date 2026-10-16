from __future__ import annotations

from typing import Any

from app.models.resolution import ResolutionResult
from app.registry.access import get_capability



USER_FACING_PRODUCT_COPY = {
    "curpify": {
        "title": "Curpify",
        "summary": "API de validación estructural de CURP y RFC para México, con normalización y verificación de formato y dígitos de control.",
        "context": "Permite integrar validaciones de identidad y datos fiscales en aplicaciones mediante API key. La validación estructural no equivale a consultar o certificar registros oficiales.",
        "next_step": "Puedo explicarte cómo obtener tu API key o integrar las validaciones en tu aplicación.",
        "offer_help": "Puedo ayudarte con ejemplos de integración, formatos admitidos y uso de la API.",
    },
    "evilink_overview": {
        "title": "Evilink",
        "summary": "Ecosistema modular de APIs y productos enfocados en datos, validación, criptografía, observabilidad e inteligencia de mercado.",
        "context": "Incluye CryptoLink, Curpify, Data_Link, V-Secrets y Status-Hub, además de servicios especializados y componentes de integración como Nexus, evi-gateway y MCP-One. Cada producto tiene capacidades y niveles de madurez diferentes.",
        "next_step": "Puedo explicarte qué hace cada producto y cómo se relaciona con el ecosistema.",
        "offer_help": "Puedo ayudarte a identificar qué producto encaja mejor con tu necesidad.",
    },
    "datalink": {
        "title": "Data_Link",
        "summary": "Plataforma de procesamiento y transformación de datos estructurados, con operaciones de limpieza, deduplicación, filtrado y conversión.",
        "context": "Su API y portal permiten trabajar con archivos CSV y JSON, aplicar transformaciones y preparar datos para otros sistemas. Incluye capacidades de procesamiento mediante jobs; el rendimiento depende del tamaño y tipo de archivo y de la operación solicitada.",
        "next_step": "Puedo explicarte cómo utilizar Data_Link para limpiar, transformar o preparar tus datos.",
        "offer_help": "Puedo orientarte sobre sus operaciones, formatos admitidos e integración mediante API.",
    },
    "v_secrets": {
        "title": "V-Secrets",
        "summary": "Servicio de gestión segura de secretos, credenciales y API keys para aplicaciones y proyectos.",
        "context": "Dispone de API y portal propio, cifrado de secretos y mecanismos de autenticación y control de acceso. Está diseñado para centralizar material sensible y reducir la exposición de credenciales dentro de aplicaciones.",
        "next_step": "Puedo explicarte cómo organizar tus secretos, administrar credenciales e integrar V-Secrets.",
        "offer_help": "Puedo orientarte sobre integración, gestión de claves y buenas prácticas de seguridad.",
    },
    "cryptolink": {
        "title": "CryptoLink",
        "summary": "Plataforma de información e inteligencia de mercado cripto con cotizaciones, datos históricos, tendencias e indicadores derivados.",
        "context": "CryptoLink API V2 combina datos de proveedores externos con persistencia histórica y cálculos propios. Su portal presenta precios, Overview, Momentum, Market Breadth y otras vistas de mercado. Algunas capacidades son especializadas y la API V3, junto con sus futuros planes comerciales, continúa en preparación.",
        "next_step": "Puedes preguntarme por cotizaciones, gráficas recientes, momentum o señales disponibles, por ejemplo: 'muéstrame la gráfica de precio de BTC'.",
        "offer_help": "Puedo ayudarte a consultar y comprender los indicadores de mercado disponibles mediante Nexus.",
    },
    "social_link": {
        "title": "Social_Link",
        "summary": "Servicio de inteligencia de atención y tendencias del mercado cripto, basado en señales recopiladas y datos históricos.",
        "context": "Complementa a CryptoLink mediante capacidades como Trending Now y Market Attention. Permite observar qué activos reciben atención y cómo evoluciona esa atención durante un periodo. Sus capacidades de análisis mediante machine learning continúan en desarrollo.",
        "next_step": "Puedo explicarte cómo se diferencian las tendencias, la atención histórica y los precios de mercado.",
        "offer_help": "Puedo ayudarte a entender las señales de Social_Link y su relación con CryptoLink.",
    },
    "status_hub": {
        "title": "Status-Hub",
        "summary": "Servicio de observabilidad para conocer el estado operativo y detectar degradaciones de aplicaciones del ecosistema Evilink.",
        "context": "Supervisa disponibilidad y señales de salud de distintos servicios, con estados como operational, degraded, maintenance y down. Ha permitido detectar incidentes reales y apoyar el diagnóstico operativo.",
        "next_step": "Puedo explicarte cómo se interpretan los estados y qué información proporciona Status-Hub.",
        "offer_help": "Puedo orientarte sobre monitoreo, disponibilidad y diagnóstico de incidentes.",
    },
    "secure_link": {
        "title": "Secure_Link",
        "summary": "Proyecto de evaluación de riesgo orientado a detectar patrones sospechosos mediante reglas y modelos de análisis.",
        "context": "Contempla señales relacionadas con accesos, dispositivos, velocidad de eventos y comportamientos anómalos. Cuenta con componentes desarrollados, pero permanece en una etapa de maduración y no debe presentarse como un producto de lanzamiento comercial general.",
        "next_step": "Puedo explicarte los escenarios de riesgo que busca resolver y el alcance de su desarrollo.",
        "offer_help": "Puedo ayudarte a entender el enfoque de Secure_Link y sus capacidades previstas.",
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