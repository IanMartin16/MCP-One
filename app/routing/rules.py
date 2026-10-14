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
    candidate_matches: list[str] | None = None,
    current_matches: list[str] | None = None,
) -> bool:
    if current_rule is None:
        return True

    # 1. Primero: especificidad REAL del pattern que hizo match.
    candidate_match_specificity = matched_specificity_score(
        candidate_matches
    )
    current_match_specificity = matched_specificity_score(
        current_matches
    )

    if candidate_match_specificity > current_match_specificity:
        return True

    if candidate_match_specificity < current_match_specificity:
        return False

    # 2. Si la especificidad empató, cantidad de matches.
    if candidate_match_count > current_match_count:
        return True

    if candidate_match_count < current_match_count:
        return False

    # 3. Priority declarada.
    candidate_priority = rule_priority_score(candidate_rule)
    current_priority = rule_priority_score(current_rule)

    if candidate_priority > current_priority:
        return True

    if candidate_priority < current_priority:
        return False

    # 4. Último desempate: especificidad global de la regla.
    candidate_specificity = specificity_score(candidate_rule)
    current_specificity = specificity_score(current_rule)

    return candidate_specificity > current_specificity

def matched_specificity_score(
    matched_patterns: list[str] | None,
) -> tuple[int, int]:
    """
    Prioriza el patrón que realmente hizo match.

    Ej:
      "gráfica de precio" -> (3 palabras, 17 chars)
      "precio de"         -> (2 palabras, 9 chars)
      "precio"            -> (1 palabra, 6 chars)
    """
    if not matched_patterns:
        return (0, 0)

    longest = max(
        matched_patterns,
        key=lambda p: (len(p.split()), len(p)),
    )

    return (
        len(longest.split()),
        len(longest),
    )    