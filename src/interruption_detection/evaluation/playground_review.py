from __future__ import annotations

import json
import os
from typing import Any, Literal, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import Field

from interruption_detection.llm import LLMError
from interruption_detection.models import (
    ActionLabel,
    PolicyDecision,
    StrictModel,
    UserToneHint,
)


ReviewVerdict = Literal["agree", "disagree", "uncertain"]


class PlaygroundReviewInput(StrictModel):
    """Playground에서 단일 policy decision을 LLM review에 넘길 runtime 입력."""

    ai_current_intent: str
    ai_utterance: str
    user_utterance: str
    user_tone_hint: UserToneHint = UserToneHint.NEUTRAL
    has_user_speech: bool
    decision: PolicyDecision


class PlaygroundReviewRequest(StrictModel):
    """LLM review client에 전달할 prompt와 추적 메타데이터."""

    prompt_version: str
    developer_prompt: str
    user_prompt: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class PlaygroundReviewJudgment(StrictModel):
    """LLM이 판단한 Playground용 policy decision review."""

    verdict: ReviewVerdict
    recommended_action: ActionLabel | None
    confidence: float | None = Field(default=None, ge=0, le=1)
    reason: str
    reviewer_steps: list[str] = Field(default_factory=list)


class PlaygroundReviewResult(PlaygroundReviewJudgment):
    """API 응답에 provider snapshot을 덧붙인 review 결과."""

    reviewer_snapshot: dict[str, Any]


class PlaygroundReviewClient(Protocol):
    """Playground review가 의존하는 최소 LLM client 인터페이스."""

    def review(self, request: PlaygroundReviewRequest) -> PlaygroundReviewJudgment:
        """prompt를 실행해 Playground review judgment를 반환한다."""
        ...

    def snapshot(self) -> dict[str, object]:
        """review 응답에 남길 provider/model 설정을 반환한다."""
        ...


PLAYGROUND_REVIEW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["agree", "disagree", "uncertain"],
        },
        "recommended_action": {
            "type": ["string", "null"],
            "enum": [label.value for label in ActionLabel] + [None],
        },
        "confidence": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "reason": {"type": "string"},
        "reviewer_steps": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "verdict",
        "recommended_action",
        "confidence",
        "reason",
        "reviewer_steps",
    ],
    "additionalProperties": False,
}


class OpenAIResponsesPlaygroundReviewClient:
    """OpenAI Responses API를 직접 호출하는 Playground review client."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_s: float | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.model = (
            model
            or os.getenv("OPENAI_REVIEW_MODEL")
            or os.getenv("OPENAI_ACTION_MODEL", "gpt-5.4-mini")
        )
        self.base_url = (
            base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com"
        ).rstrip("/")
        self.timeout_s = timeout_s or float(os.getenv("OPENAI_REVIEW_TIMEOUT_S", "30"))

    def review(self, request: PlaygroundReviewRequest) -> PlaygroundReviewJudgment:
        """Responses API structured output을 호출해 review judgment로 검증한다."""
        if not self.api_key:
            raise LLMError("OPENAI_API_KEY is required for Playground LLM review")

        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "developer",
                    "content": [
                        {"type": "input_text", "text": request.developer_prompt}
                    ],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": request.user_prompt}],
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "playground_review",
                    "strict": True,
                    "schema": PLAYGROUND_REVIEW_SCHEMA,
                }
            },
            "max_output_tokens": 500,
        }

        raw = self._post_json("/v1/responses", payload)
        output_text = _extract_output_text(raw)

        try:
            parsed = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise LLMError("LLM review response was not valid JSON") from exc

        return PlaygroundReviewJudgment.model_validate(parsed)

    def snapshot(self) -> dict[str, object]:
        """Provider 설정을 Playground review 응답에 남길 형태로 반환한다."""
        return {
            "provider": "openai_responses",
            "model": self.model,
            "base_url": self.base_url,
            "response_format": "json_schema",
            "timeout_s": self.timeout_s,
        }

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout_s) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMError(f"OpenAI Responses API error: {exc.code} {detail}") from exc
        except URLError as exc:
            raise LLMError(
                f"OpenAI Responses API request failed: {exc.reason}"
            ) from exc


def review_playground_decision(
    review_input: PlaygroundReviewInput,
    *,
    client: PlaygroundReviewClient | None = None,
) -> PlaygroundReviewResult:
    """Playground 단일 decision을 runtime context 기준으로 LLM review한다."""
    reviewer = client or OpenAIResponsesPlaygroundReviewClient()
    request = PlaygroundReviewRequest(
        prompt_version="playground_policy_review_v1",
        developer_prompt=_developer_prompt(),
        user_prompt=_user_prompt(review_input),
        metadata={
            "input_fields": [
                "ai_current_intent",
                "ai_utterance",
                "user_utterance",
                "user_tone_hint",
                "has_user_speech",
                "decision.policy_name",
                "decision.actual_action",
                "decision.reason",
                "decision.signals",
            ],
            "surface": "playground",
            "official_metric": False,
        },
    )
    judgment = reviewer.review(request)

    return PlaygroundReviewResult(
        **judgment.model_dump(),
        reviewer_snapshot=reviewer.snapshot(),
    )


def _developer_prompt() -> str:
    allowed_action_labels = ", ".join(label.value for label in ActionLabel)

    return "\n".join(
        [
            "You review one interruption policy decision for a Korean commerce "
            "support assistant Playground.",
            "Judge only whether the selected action is reasonable for the supplied "
            "runtime transcript and policy reason.",
            f"Allowed recommended_action values: {allowed_action_labels}, or null.",
            "Do not assume hidden scenario labels or benchmark answers.",
            "This review is a developer debugging aid, not an official metric.",
            "Return a concise reason in English or Korean.",
        ]
    )


def _user_prompt(review_input: PlaygroundReviewInput) -> str:
    context = {
        "ai_current_intent": review_input.ai_current_intent,
        "ai_utterance": review_input.ai_utterance,
        "user_utterance": review_input.user_utterance,
        "user_tone_hint": review_input.user_tone_hint.value,
        "has_user_speech": review_input.has_user_speech,
        "policy_decision": {
            "policy_name": review_input.decision.policy_name,
            "actual_action": review_input.decision.actual_action.value,
            "reason": review_input.decision.reason,
            "signal_summary": _signal_summary(review_input.decision.signals),
        },
    }

    return (
        "Review the policy decision for this single interruption moment.\n"
        "Runtime context JSON:\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}"
    )


def _signal_summary(signals: dict[str, Any]) -> dict[str, Any]:
    allowed_keys = [
        "predicted_user_intent",
        "confidence",
        "ambiguity",
        "signal_source",
        "input_mode",
        "input_adapter",
    ]

    return {key: signals[key] for key in allowed_keys if key in signals}


def _extract_output_text(response: dict[str, Any]) -> str:
    output_text = response.get("output_text")

    if isinstance(output_text, str) and output_text.strip():
        return output_text

    for item in response.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue

        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue

            text = content.get("text")

            if isinstance(text, str) and text.strip():
                return text

    raise LLMError("OpenAI Responses API response did not contain output text")
