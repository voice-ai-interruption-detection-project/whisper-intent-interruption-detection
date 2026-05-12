from __future__ import annotations

import json
import os
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from pydantic import Field

from interruption_detection.models import ActionLabel, EventType, StrictModel

load_dotenv()


class LLMError(ValueError):
    """LLM action judgment boundary에서 발생한 오류."""


class LLMActionJudgment(StrictModel):
    """LLM이 해석한 고객 신호와 선택한 action label."""

    actual_action: ActionLabel
    reason: str
    confidence: float | None = Field(default=None, ge=0, le=1)
    predicted_event_type: EventType | None = None
    predicted_user_intent: str | None = None
    ambiguity: str | None = None
    interpreter_steps: list[str] = Field(default_factory=list)
    interpreted_user_intent: str | None = None
    is_intent_shift: bool | None = None


class LLMActionRequest(StrictModel):
    """LLM action judge에 전달하는 prompt와 추적 메타데이터."""

    policy_name: str
    prompt_version: str
    developer_prompt: str
    user_prompt: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMActionClient(Protocol):
    """정책이 의존하는 최소 LLM client 인터페이스."""

    def judge_action(self, request: LLMActionRequest) -> LLMActionJudgment:
        """LLM prompt를 실행해 action judgment를 반환한다."""
        ...

    def snapshot(self) -> dict[str, object]:
        """run artifact에 남길 provider/model 설정을 반환한다."""
        ...


ACTION_JUDGMENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "actual_action": {
            "type": "string",
            "enum": [label.value for label in ActionLabel],
        },
        "reason": {"type": "string"},
        "confidence": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "predicted_event_type": {
            "type": ["string", "null"],
            "enum": [item.value for item in EventType] + [None],
        },
        "predicted_user_intent": {"type": ["string", "null"]},
        "ambiguity": {"type": ["string", "null"]},
        "interpreter_steps": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "actual_action",
        "reason",
        "confidence",
        "predicted_event_type",
        "predicted_user_intent",
        "ambiguity",
        "interpreter_steps",
    ],
    "additionalProperties": False,
}


class OpenAIResponsesLLMClient:
    """OpenAI Responses API를 직접 호출하는 얇은 action judge client."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_s: float | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_ACTION_MODEL", "gpt-5.4-mini")
        self.base_url = (
            base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com"
        ).rstrip("/")
        self.timeout_s = timeout_s or float(os.getenv("OPENAI_ACTION_TIMEOUT_S", "30"))

    def judge_action(self, request: LLMActionRequest) -> LLMActionJudgment:
        """Responses API structured output을 호출해 action judgment로 검증한다."""
        if not self.api_key:
            raise LLMError("OPENAI_API_KEY is required for LLM action judgment")

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
                    "name": "action_judgment",
                    "strict": True,
                    "schema": ACTION_JUDGMENT_SCHEMA,
                }
            },
            "max_output_tokens": 700,
        }

        raw = self._post_json("/v1/responses", payload)
        output_text = _extract_output_text(raw)

        try:
            parsed = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise LLMError("LLM response was not valid JSON") from exc

        return LLMActionJudgment.model_validate(parsed)

    def snapshot(self) -> dict[str, object]:
        """Provider 설정을 결과 artifact에 남길 형태로 반환한다."""
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


def _extract_output_text(response: dict[str, Any]) -> str:
    """Responses API HTTP 응답에서 텍스트 payload를 최대한 보수적으로 꺼낸다."""
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
