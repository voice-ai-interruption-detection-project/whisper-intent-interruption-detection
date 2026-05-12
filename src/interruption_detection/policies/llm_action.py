from __future__ import annotations

import json

from interruption_detection.action_selector.llm import LLMBaselineActionSelector
from interruption_detection.interpreter.llm import LLMStructuredSignalInterpreter
from interruption_detection.llm import (
    LLMActionClient,
    LLMActionJudgment,
    LLMActionRequest,
    OpenAIResponsesLLMClient,
)
from interruption_detection.models import (
    ActionLabel,
    EventType,
    PolicyDecision,
    PolicyInput,
)
from interruption_detection.pipelines.decision_pipeline import DecisionPipeline


ACTION_LABEL_DEFINITIONS: dict[ActionLabel, str] = {
    ActionLabel.CONTINUE: (
        "Continue the AI utterance when there is no meaningful user request, only "
        "silence/noise, or a brief acknowledgement that does not need a response."
    ),
    ActionLabel.BRIEF_ACK: (
        "Briefly acknowledge a short backchannel, then continue the original AI flow."
    ),
    ActionLabel.RESPOND_AND_CONTINUE: (
        "Answer a same-topic follow-up question, then continue the original flow."
    ),
    ActionLabel.STOP_AND_SWITCH: (
        "Stop the current AI utterance and switch to the user's new intent."
    ),
    ActionLabel.ASK_CLARIFYING: (
        "Ask a clarifying question when the user signal is too ambiguous to route."
    ),
    ActionLabel.HANDOFF: (
        "Route toward a human agent for urgent, severe, or explicit agent requests."
    ),
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
        "actual_action": "stop_and_switch",
        "reason": "The user is changing from shipping status to a refund request.",
    },
    {
        "input": {
            "ai_current_intent": "shipping_inquiry",
            "ai_utterance": "Your item is in transit and will arrive tomorrow.",
            "user_utterance": "How much is shipping?",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "actual_action": "respond_and_continue",
        "reason": "The user asks a same-topic shipping follow-up.",
    },
    {
        "input": {
            "ai_current_intent": "product_inquiry",
            "ai_utterance": "The product comes in M, L, and XL.",
            "user_utterance": "네.",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "actual_action": "continue",
        "reason": "The user only acknowledges, so no interruption is needed.",
    },
]


class LegacyLLMActionJudgmentProvider:
    """one-shot LLM structured output을 baseline action candidate로 제공한다."""

    def __init__(
        self,
        *,
        policy_name: str,
        prompt_version: str,
        include_label_definitions: bool,
        include_few_shots: bool,
        include_tone_hint: bool,
        llm_client: LLMActionClient | None = None,
    ) -> None:
        self.name = "legacy_llm_action_judgment_provider"
        self.policy_name = policy_name
        self.prompt_version = prompt_version
        self.include_label_definitions = include_label_definitions
        self.include_few_shots = include_few_shots
        self.include_tone_hint = include_tone_hint
        self._llm_client = llm_client or OpenAIResponsesLLMClient()

    def judge(self, policy_input: PolicyInput) -> LLMActionJudgment:
        """legacy one-shot prompt로 LLM action judgment 후보를 반환한다."""
        request = LLMActionRequest(
            policy_name=self.policy_name,
            prompt_version=self.prompt_version,
            developer_prompt=self._developer_prompt(),
            user_prompt=self._user_prompt(policy_input),
            metadata={
                "input_fields": self._input_fields(),
                "excluded_fields": [
                    "expected_action",
                    "event_type",
                    "expected_user_intent",
                ],
            },
        )

        return self._llm_client.judge_action(request)

    def snapshot(self) -> dict[str, object]:
        """provider 설정을 run artifact에 남긴다."""
        return {
            "name": self.name,
            "policy_name": self.policy_name,
            "prompt_version": self.prompt_version,
            "llm": self._client_snapshot(),
            "input_fields": self._input_fields(),
            "excluded_fields": [
                "expected_action",
                "event_type",
                "expected_user_intent",
            ],
            "structured_output": "action_judgment_with_signal_interpretation",
        }

    def input_fields(self) -> list[str]:
        """LLM prompt에 포함되는 runtime 입력 필드 목록을 반환한다."""
        return self._input_fields()

    def excluded_fields(self) -> list[str]:
        """LLM prompt에서 제외되는 평가/라벨 필드 목록을 반환한다."""
        return [
            "expected_action",
            "event_type",
            "expected_user_intent",
        ]

    def _developer_prompt(self) -> str:
        allowed_action_labels = ", ".join(label.value for label in ActionLabel)
        allowed_event_types = ", ".join(item.value for item in EventType)

        parts = [
            "You are the AI Action Policy for a Korean commerce support assistant.",
            "Work in two layers: first interpret the customer's runtime signal, "
            "then choose the assistant's next action.",
            f"Allowed action labels: {allowed_action_labels}.",
            f"Allowed predicted_event_type values: {allowed_event_types}, "
            "or null when no event type is appropriate.",
            "Base your decision only on the supplied text transcript and metadata.",
            "Do not infer from hidden expected answers, event_type labels, or evaluation labels.",
            "Return predicted_event_type, predicted_user_intent, confidence, "
            "ambiguity, interpreter_steps, actual_action, and reason.",
            "Return a concise reason in English or Korean.",
        ]

        if self.include_label_definitions:
            definitions = "\n".join(
                f"- {label.value}: {text}"
                for label, text in ACTION_LABEL_DEFINITIONS.items()
            )
            parts.append(f"Action label definitions:\n{definitions}")

        if self.include_few_shots:
            parts.append(
                "Examples:\n"
                + json.dumps(FEW_SHOT_EXAMPLES, ensure_ascii=False, indent=2)
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
            "Classify the assistant's next action for this single interruption moment.\n"
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
        llm_client: LLMActionClient | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.prompt_version = prompt_version
        self._judgment_provider = LegacyLLMActionJudgmentProvider(
            policy_name=name,
            prompt_version=prompt_version,
            include_label_definitions=include_label_definitions,
            include_few_shots=include_few_shots,
            include_tone_hint=include_tone_hint,
            llm_client=llm_client,
        )
        self._pipeline = DecisionPipeline(
            policy_name=name,
            prompt_version=prompt_version,
            judgment_provider=self._judgment_provider,
            interpreter=LLMStructuredSignalInterpreter(),
            action_selector=LLMBaselineActionSelector(),
        )

    def predict(self, policy_input: PolicyInput) -> PolicyDecision:
        """policy용 runtime 입력으로 pipeline 판단 결과를 반환한다."""
        return self._pipeline.run(policy_input)

    def snapshot(self) -> dict[str, object]:
        """LLM-backed pipeline 정책 설정을 run artifact에 남긴다."""
        provider_snapshot = self._judgment_provider.snapshot()

        return {
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
