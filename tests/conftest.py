from __future__ import annotations

import json
from typing import Any

import pytest

from interruption_detection.llm import LLMActionJudgment, LLMActionRequest
from interruption_detection.models import ActionLabel, EventType
from interruption_detection.policies import (
    build_policy_registry,
    replace_policy_registry_for_testing,
    reset_policy_registry,
)


class KeywordFakeLLMClient:
    """테스트에서 실제 API 호출 없이 transcript 기반 판단을 흉내낸다."""

    def __init__(self) -> None:
        self.requests: list[LLMActionRequest] = []

    def judge_action(self, request: LLMActionRequest) -> LLMActionJudgment:
        self.requests.append(request)
        context = _extract_context(request.user_prompt)
        user_utterance = str(context.get("user_utterance") or "").lower()
        current_intent = str(context.get("ai_current_intent") or "").lower()
        has_speech = bool(context.get("has_user_speech"))

        if not has_speech or not user_utterance.strip():
            return _judgment(
                ActionLabel.CONTINUE,
                "No user speech to classify.",
                event_type=EventType.NO_SPEECH,
                ambiguity="low",
            )

        if any(term in user_utterance for term in ["refund", "환불", "반품"]):
            return _judgment(
                ActionLabel.STOP_AND_SWITCH,
                "User transcript asks for a different commerce intent.",
                "refund_or_return",
                EventType.INTENT_SHIFT,
                "low",
            )

        if any(term in user_utterance for term in ["agent", "human", "사람"]):
            return _judgment(
                ActionLabel.HANDOFF,
                "User transcript asks for a human agent.",
                "agent_connection",
                EventType.COMPLAINT,
                "medium",
            )

        if any(term in user_utterance for term in ["shipping", "배송", "추적번호"]):
            is_shift = "shipping" not in current_intent
            action = (
                ActionLabel.STOP_AND_SWITCH
                if is_shift
                else ActionLabel.RESPOND_AND_CONTINUE
            )
            event_type = (
                EventType.INTENT_SHIFT if is_shift else EventType.SAME_INTENT_QUESTION
            )
            return _judgment(
                action,
                "User transcript is about shipping.",
                "shipping",
                event_type,
                "low",
            )

        if user_utterance in {"ok", "네.", "네", "알겠어요.", "알겠어요"}:
            return _judgment(
                ActionLabel.CONTINUE,
                "Short acknowledgement.",
                event_type=EventType.BACKCHANNEL,
                ambiguity="low",
            )

        return _judgment(
            ActionLabel.ASK_CLARIFYING,
            "User transcript is ambiguous.",
            event_type=EventType.AMBIGUOUS,
            ambiguity="high",
        )

    def snapshot(self) -> dict[str, object]:
        return {
            "provider": "fake",
            "model": "keyword-fake",
            "response_format": "json_schema",
        }


@pytest.fixture()
def fake_llm_client() -> KeywordFakeLLMClient:
    return KeywordFakeLLMClient()


@pytest.fixture(autouse=True)
def fake_policy_registry(fake_llm_client: KeywordFakeLLMClient):
    replace_policy_registry_for_testing(build_policy_registry(fake_llm_client))

    try:
        yield
    finally:
        reset_policy_registry()


def _extract_context(user_prompt: str) -> dict[str, Any]:
    _, _, raw_json = user_prompt.partition("Input context JSON:")

    return json.loads(raw_json.strip())


def _judgment(
    action: ActionLabel,
    reason: str,
    intent: str | None = None,
    event_type: EventType | None = None,
    ambiguity: str | None = None,
) -> LLMActionJudgment:
    return LLMActionJudgment(
        actual_action=action,
        reason=reason,
        confidence=0.88,
        predicted_event_type=event_type,
        predicted_user_intent=intent,
        ambiguity=ambiguity,
        interpreter_steps=["read_transcript", "classify_customer_signal"],
    )
