from __future__ import annotations

from app.models.registry import IntentRule


PRIORITY_WEIGHT = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def rule_priority_score(rule: IntentRule) -> int:
    return PRIORITY_WEIGHT.get(rule.priority, 0)


def specificity_score(rule: IntentRule) -> int:
    score = 0

    for pattern in rule.patterns:
        score += 2 if " " in pattern else 1

    score += len(rule.preferred_capabilities) * 2
    return score


def compare_rules(
    candidate_rule: IntentRule,
    candidate_match_count: int,
    current_rule: IntentRule | None,
    current_match_count: int,
) -> bool:
    if current_rule is None:
        return True

    if candidate_match_count > current_match_count:
        return True

    if candidate_match_count < current_match_count:
        return False

    candidate_priority = rule_priority_score(candidate_rule)
    current_priority = rule_priority_score(current_rule)

    if candidate_priority > current_priority:
        return True

    if candidate_priority < current_priority:
        return False

    candidate_specificity = specificity_score(candidate_rule)
    current_specificity = specificity_score(current_rule)

    if candidate_specificity > current_specificity:
        return True

    return False