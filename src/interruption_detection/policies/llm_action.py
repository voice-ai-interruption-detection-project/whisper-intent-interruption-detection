from __future__ import annotations

import json

from interruption_detection.action_selector.rule_based import RuleBasedActionSelector
from interruption_detection.interpreter.llm import LLMStructuredSignalInterpreter
from interruption_detection.llm import (
    LLMSignalClient,
    LLMSignalJudgment,
    LLMSignalRequest,
    OpenAIResponsesLLMClient,
)
from interruption_detection.models import EventType, PolicyDecision, PolicyInput
from interruption_detection.pipelines.decision_pipeline import DecisionPipeline


EVENT_TYPE_DEFINITIONS: dict[EventType, str] = {
    EventType.NO_SPEECH: "No user speech is present.",
    EventType.NOISE: "Sound is present, but no meaningful user utterance is present.",
    EventType.BACKCHANNEL: (
        "A short acknowledgement such as 네, 알겠습니다, 맞아요, or thanks."
    ),
    EventType.SAME_INTENT_QUESTION: (
        "The user asks a follow-up question about the assistant's current intent."
    ),
    EventType.INTENT_SHIFT: (
        "The user introduces a different task, request, or target intent."
    ),
    EventType.COMPLAINT: "The user expresses dissatisfaction or escalation.",
    EventType.AMBIGUOUS: "The user signal is too unclear to route confidently.",
}


FEW_SHOT_EXAMPLES = [
    {
        "input": {
            "ai_current_intent": "shipping_inquiry",
            "ai_utterance": "Your item is in transit and will arrive tomorrow.",
            "user_utterance": "I want a refund instead.",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "predicted_event_type": "intent_shift",
        "predicted_user_intent": "refund_request",
        "ambiguity": "low",
    },
    {
        "input": {
            "ai_current_intent": "shipping_inquiry",
            "ai_utterance": "Your item is in transit and will arrive tomorrow.",
            "user_utterance": "How much is shipping?",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "predicted_event_type": "same_intent_question",
        "predicted_user_intent": "shipping_inquiry",
        "ambiguity": "low",
    },
    {
        "input": {
            "ai_current_intent": "product_inquiry",
            "ai_utterance": "The product comes in M, L, and XL.",
            "user_utterance": "네.",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "predicted_event_type": "backchannel",
        "predicted_user_intent": None,
        "ambiguity": "low",
    },
]


EXCLUDED_PROMPT_FIELDS = [
    "expected_actions",
    "event_type",
    "expected_user_intent",
]


class LLMSignalJudgmentProvider:
    """LLM structured output으로 runtime 고객 신호만 해석한다."""

    def __init__(
        self,
        *,
        policy_name: str,
        prompt_version: str,
        include_label_definitions: bool,
        include_few_shots: bool,
        include_tone_hint: bool,
        policy_guidance: dict[str, object] | None = None,
        extra_few_shots: list[dict[str, object]] | None = None,
        llm_client: LLMSignalClient | None = None,
    ) -> None:
        self.name = "llm_signal_judgment_provider"
        self.policy_name = policy_name
        self.prompt_version = prompt_version
        self.include_label_definitions = include_label_definitions
        self.include_few_shots = include_few_shots
        self.include_tone_hint = include_tone_hint
        self.policy_guidance = policy_guidance
        self.extra_few_shots = extra_few_shots or []
        self._llm_client = llm_client or OpenAIResponsesLLMClient()

    def judge(self, policy_input: PolicyInput) -> LLMSignalJudgment:
        """LLM prompt로 고객 신호 해석 결과를 반환한다."""
        metadata = {
            "input_fields": self._input_fields(),
            "excluded_fields": self.excluded_fields(),
        }

        if self.policy_guidance is not None:
            metadata["policy_guidance"] = self.policy_guidance

        request = LLMSignalRequest(
            policy_name=self.policy_name,
            prompt_version=self.prompt_version,
            developer_prompt=self._developer_prompt(),
            user_prompt=self._user_prompt(policy_input),
            metadata=metadata,
        )

        return self._llm_client.interpret_signal(request)

    def snapshot(self) -> dict[str, object]:
        """provider 설정을 run artifact에 남긴다."""
        snapshot = {
            "name": self.name,
            "policy_name": self.policy_name,
            "prompt_version": self.prompt_version,
            "llm": self._client_snapshot(),
            "input_fields": self._input_fields(),
            "excluded_fields": self.excluded_fields(),
            "structured_output": "signal_interpretation",
        }

        if self.policy_guidance is not None:
            snapshot["policy_guidance"] = self.policy_guidance

        return snapshot

    def input_fields(self) -> list[str]:
        """LLM prompt에 포함되는 runtime 입력 필드 목록을 반환한다."""
        return self._input_fields()

    def excluded_fields(self) -> list[str]:
        """LLM prompt에서 제외되는 평가/라벨 필드 목록을 반환한다."""
        return list(EXCLUDED_PROMPT_FIELDS)

    def _developer_prompt(self) -> str:
        allowed_event_types = ", ".join(item.value for item in EventType)

        parts = [
            "You are the AI Action Policy for a Korean commerce support assistant.",
            "Interpret the customer's runtime signal. Do not choose the assistant's "
            "next action.",
            f"Allowed predicted_event_type values: {allowed_event_types}, "
            "or null when no event type is appropriate.",
            "Base your decision only on the supplied text transcript and metadata.",
            "Do not infer from hidden expected answers, event_type labels, or evaluation labels.",
            "Return only predicted_event_type, predicted_user_intent, confidence, "
            "ambiguity, and interpreter_steps.",
        ]

        if self.include_label_definitions:
            definitions = "\n".join(
                f"- {event_type.value}: {text}"
                for event_type, text in EVENT_TYPE_DEFINITIONS.items()
            )
            parts.append(f"Customer signal label definitions:\n{definitions}")

        if self.policy_guidance is not None:
            parts.append(
                "Policy-specific guidance:\n"
                + json.dumps(self.policy_guidance, ensure_ascii=False, indent=2)
            )

        if self.include_few_shots:
            examples = [*FEW_SHOT_EXAMPLES, *self.extra_few_shots]
            parts.append(
                "Examples:\n" + json.dumps(examples, ensure_ascii=False, indent=2)
            )

        return "\n\n".join(parts)

    def _user_prompt(self, policy_input: PolicyInput) -> str:
        context = {
            "ai_current_intent": policy_input.ai_current_intent,
            "ai_utterance": policy_input.ai_utterance,
            "user_utterance": policy_input.user_utterance,
            "has_user_speech": policy_input.has_user_speech,
        }

        if self.include_tone_hint:
            context["user_tone_hint"] = policy_input.user_tone_hint.value

        return (
            "Interpret the customer signal for this single interruption moment.\n"
            "Input context JSON:\n"
            f"{json.dumps(context, ensure_ascii=False, indent=2)}"
        )

    def _input_fields(self) -> list[str]:
        fields = [
            "ai_current_intent",
            "ai_utterance",
            "user_utterance",
            "has_user_speech",
        ]

        if self.include_tone_hint:
            fields.append("user_tone_hint")

        return fields

    def _client_snapshot(self) -> dict[str, object]:
        return self._llm_client.snapshot()


class LLMActionPolicy:
    """기존 policy registry 호환을 위한 decision pipeline wrapper."""

    def __init__(
        self,
        *,
        name: str,
        description: str,
        prompt_version: str,
        include_label_definitions: bool,
        include_few_shots: bool,
        include_tone_hint: bool,
        policy_guidance: dict[str, object] | None = None,
        extra_few_shots: list[dict[str, object]] | None = None,
        llm_client: LLMSignalClient | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.prompt_version = prompt_version
        self._judgment_provider = LLMSignalJudgmentProvider(
            policy_name=name,
            prompt_version=prompt_version,
            include_label_definitions=include_label_definitions,
            include_few_shots=include_few_shots,
            include_tone_hint=include_tone_hint,
            policy_guidance=policy_guidance,
            extra_few_shots=extra_few_shots,
            llm_client=llm_client,
        )
        self._pipeline = DecisionPipeline(
            policy_name=name,
            prompt_version=prompt_version,
            judgment_provider=self._judgment_provider,
            interpreter=LLMStructuredSignalInterpreter(),
            action_selector=RuleBasedActionSelector(),
        )

    def predict(self, policy_input: PolicyInput) -> PolicyDecision:
        """policy용 runtime 입력으로 pipeline 판단 결과를 반환한다."""
        return self._pipeline.run(policy_input)

    def snapshot(self) -> dict[str, object]:
        """LLM-backed pipeline 정책 설정을 run artifact에 남긴다."""
        provider_snapshot = self._judgment_provider.snapshot()

        snapshot = {
            "name": self.name,
            "version": "pipeline-components-v1",
            "mode": "interpreter_pipeline_action_selector",
            "prompt_version": self.prompt_version,
            "llm": provider_snapshot["llm"],
            "pipeline": self._pipeline.snapshot(),
            "input_fields": self._judgment_provider.input_fields(),
            "excluded_fields": self._judgment_provider.excluded_fields(),
            "structured_output": provider_snapshot["structured_output"],
        }

        if "policy_guidance" in provider_snapshot:
            snapshot["policy_guidance"] = provider_snapshot["policy_guidance"]

        return snapshot
