from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from app.models.registry import IntentRule
from app.registry.access import get_all_rules
from app.routing.rules import compare_rules


@dataclass
class MatchResult:
    intent_family: Optional[str]
    matched_rule: Optional[IntentRule]
    confidence: float
    matched_patterns: list[str]


def _normalize_text(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"\s+", " ", value)
    return value


def _pattern_matches(text: str, pattern: str) -> bool:
    pattern = pattern.lower().strip()
    if not pattern:
        return False

    escaped = re.escape(pattern)

    if " " in pattern:
        return re.search(rf"\b{escaped}\b", text) is not None

    return re.search(rf"\b{escaped}\b", text) is not None


def detect_intent_family(user_input: str) -> MatchResult:
    text = _normalize_text(user_input)
    rules = [rule for rule in get_all_rules() if rule.enabled]

    best_rule: Optional[IntentRule] = None
    best_matches: list[str] = []
    best_score = 0

    for rule in rules:
        current_matches: list[str] = []

        for pattern in rule.patterns:
            if _pattern_matches(text, pattern):
                current_matches.append(pattern)

        current_score = len(current_matches)

        if current_score == 0:
            continue

        if compare_rules(
            candidate_rule=rule,
            candidate_match_count=current_score,
            current_rule=best_rule,
            current_match_count=best_score,
        ):
            best_rule = rule
            best_matches = current_matches
            best_score = current_score

    if not best_rule or best_score <= 0:
        return MatchResult(
            intent_family=None,
            matched_rule=None,
            confidence=0.15,
            matched_patterns=[],
        )

    total_patterns = len(best_rule.patterns) if best_rule.patterns else 1
    confidence = min(0.95, max(0.35, best_score / total_patterns + 0.25))

    if best_score == 1 and confidence < 0.35:
        return MatchResult(
            intent_family=None,
            matched_rule=None,
            confidence=0.15,
            matched_patterns=[],
        )

    return MatchResult(
        intent_family=best_rule.intent_family,
        matched_rule=best_rule,
        confidence=round(confidence, 2),
        matched_patterns=best_matches,
    )