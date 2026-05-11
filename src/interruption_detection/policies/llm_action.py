from __future__ import annotations

import json
from time import perf_counter

from interruption_detection.llm import (
    LLMActionClient,
    LLMActionRequest,
    OpenAIResponsesLLMClient,
)
from interruption_detection.models import ActionLabel, PolicyDecision, RunnerInput


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


class LLMActionPolicy:
    """텍스트 transcript를 LLM으로 판단해 action label을 고르는 공통 정책."""

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
        self.include_label_definitions = include_label_definitions
        self.include_few_shots = include_few_shots
        self.include_tone_hint = include_tone_hint
        self._llm_client = llm_client or OpenAIResponsesLLMClient()

    def predict(self, runner_input: RunnerInput) -> PolicyDecision:
        """RunnerInput을 LLM prompt로 바꾸고 action judgment를 반환한다."""
        request = LLMActionRequest(
            policy_name=self.name,
            prompt_version=self.prompt_version,
            developer_prompt=self._developer_prompt(),
            user_prompt=self._user_prompt(runner_input),
            metadata={
                "scenario_id": runner_input.scenario_id,
                "input_fields": self._input_fields(),
                "excluded_fields": [
                    "expected_action",
                    "event_type",
                    "expected_user_intent",
                ],
            },
        )
        started = perf_counter()

        judgment = self._llm_client.judge_action(request)
        llm_ms = round((perf_counter() - started) * 1000, 3)

        return PolicyDecision(
            policy_name=self.name,
            actual_action=judgment.actual_action,
            reason=judgment.reason,
            signals={
                "mode": "llm_text_action_judgment",
                "prompt_version": self.prompt_version,
                "llm": self._client_snapshot(),
                "confidence": judgment.confidence,
                "interpreted_user_intent": judgment.interpreted_user_intent,
                "is_intent_shift": judgment.is_intent_shift,
                "input_fields": self._input_fields(),
                "excluded_fields": request.metadata["excluded_fields"],
            },
            stage_latencies_ms={"llm_ms": llm_ms},
        )

    def snapshot(self) -> dict[str, object]:
        """LLM 판단 정책 설정을 run artifact에 남긴다."""
        return {
            "name": self.name,
            "version": "day3-llm-text",
            "mode": "llm_text_action_judgment",
            "prompt_version": self.prompt_version,
            "llm": self._client_snapshot(),
            "input_fields": self._input_fields(),
            "excluded_fields": [
                "expected_action",
                "event_type",
                "expected_user_intent",
            ],
            "structured_output": "action_judgment",
        }

    def _developer_prompt(self) -> str:
        allowed = ", ".join(label.value for label in ActionLabel)

        parts = [
            "You are the AI Action Policy for a Korean commerce support assistant.",
            "Your job is to choose exactly one action label for the assistant's next behavior.",
            f"Allowed action labels: {allowed}.",
            "Base your decision only on the supplied text transcript and metadata.",
            "Do not infer from hidden expected answers, event_type labels, or evaluation labels.",
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

    def _user_prompt(self, runner_input: RunnerInput) -> str:
        context = {
            "ai_current_intent": runner_input.ai_current_intent,
            "ai_utterance": runner_input.ai_utterance,
            "user_utterance": runner_input.user_utterance,
            "has_user_speech": runner_input.has_user_speech,
        }

        if self.include_tone_hint:
            context["user_tone_hint"] = runner_input.user_tone_hint.value

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
