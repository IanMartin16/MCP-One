from __future__ import annotations

from typing import Optional

from app.models.registry import CapabilityDef, IntentRule, ModuleDef
from app.registry.loader import load_registry


def get_all_modules() -> list[ModuleDef]:
    return load_registry().modules


def get_all_capabilities() -> list[CapabilityDef]:
    return load_registry().capabilities


def get_all_rules() -> list[IntentRule]:
    return load_registry().intent_rules


def get_module(module_id: str) -> Optional[ModuleDef]:
    for module in load_registry().modules:
        if module.module_id == module_id:
            return module
    return None


def get_capability(capability_id: str) -> Optional[CapabilityDef]:
    for capability in load_registry().capabilities:
        if capability.capability_id == capability_id:
            return capability
    return None


def get_rule(rule_id: str) -> Optional[IntentRule]:
    for rule in load_registry().intent_rules:
        if rule.rule_id == rule_id:
            return rule
    return None


def get_capabilities_for_module(module_id: str) -> list[CapabilityDef]:
    return [
        capability
        for capability in load_registry().capabilities
        if capability.module_id == module_id
    ]


def find_rules_by_intent_family(intent_family: str) -> list[IntentRule]:
    return [
        rule
        for rule in load_registry().intent_rules
        if rule.intent_family == intent_family and rule.enabled
    ]


def get_enabled_modules() -> list[ModuleDef]:
    return [module for module in load_registry().modules if module.enabled]


def get_enabled_capabilities() -> list[CapabilityDef]:
    return [capability for capability in load_registry().capabilities if capability.enabled]


def get_module_status(module_id: str) -> Optional[str]:
    module = get_module(module_id)
    return module.status if module else None