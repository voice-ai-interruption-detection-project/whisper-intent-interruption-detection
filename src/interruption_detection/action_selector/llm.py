from __future__ import annotations

from interruption_detection.action_selector.rule_based import RuleBasedActionSelector


class LLMBaselineActionSelector(RuleBasedActionSelector):
    """이전 import 경로 호환용 alias. 실제 선택은 rule-based selector가 맡는다."""
