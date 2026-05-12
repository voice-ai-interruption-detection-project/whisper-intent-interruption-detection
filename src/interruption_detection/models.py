from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrEnum(str, Enum):
    """JSON으로 직렬화하기 쉬운 문자열 기반 열거형."""

    def __str__(self) -> str:
        """열거형 값을 사람이 읽는 문자열로 반환한다."""
        return self.value


class ActionLabel(StrEnum):
    """정책이 최종적으로 선택할 수 있는 행동 라벨."""

    CONTINUE = "continue"
    BRIEF_ACK = "brief_ack"
    RESPOND_AND_CONTINUE = "respond_and_continue"
    STOP_AND_SWITCH = "stop_and_switch"
    ASK_CLARIFYING = "ask_clarifying"
    HANDOFF = "handoff"


class EventType(StrEnum):
    """판단 케이스(Scenario)에 기록된 고객 신호의 유형."""

    NO_SPEECH = "no_speech"
    NOISE = "noise"
    BACKCHANNEL = "backchannel"
    SAME_INTENT_QUESTION = "same_intent_question"
    INTENT_SHIFT = "intent_shift"
    COMPLAINT = "complaint"
    AMBIGUOUS = "ambiguous"


class UserToneHint(StrEnum):
    """정책 판단에 참고할 수 있는 사용자 톤 힌트."""

    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    URGENT = "urgent"


class PrimaryFailure(StrEnum):
    """예상 행동과 실제 행동이 어긋났을 때의 1차 실패 분류."""

    FALSE_STOP = "false_stop"
    MISSED_SWITCH = "missed_switch"
    ACTION_CONFUSION = "action_confusion"
    AMBIGUOUS_INTENT = "ambiguous_intent"
    STT_UNCERTAINTY = "STT_uncertainty"


class StrictModel(BaseModel):
    """기준 입력/API 경계에서 모르는 필드를 빠르게 거부하는 기본 모델."""

    # 기준 입력/API 필드가 계약에서 벗어나면 즉시 실패하게 둔다.
    model_config = ConfigDict(extra="forbid", use_enum_values=False)


class CustomerSignalInterpretation(StrictModel):
    """runtime 고객 신호 해석 결과와 디버깅용 점검값."""

    predicted_event_type: EventType | None = None
    predicted_user_intent: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    ambiguity: str | None = None
    signal_source: str
    interpreter_steps: list[str] = Field(default_factory=list)

    def to_signal_dict(self) -> dict[str, Any]:
        """run artifact의 signals에 남길 표준 키와 legacy alias를 함께 만든다."""
        payload = self.model_dump(mode="json")
        payload["interpreted_user_intent"] = self.predicted_user_intent
        payload["is_intent_shift"] = (
            self.predicted_event_type == EventType.INTENT_SHIFT
            if self.predicted_event_type is not None
            else None
        )
        payload["legacy_signal_aliases"] = {
            "interpreted_user_intent": "predicted_user_intent",
            "is_intent_shift": "predicted_event_type == intent_shift",
        }

        return payload


class ActionSelection(StrictModel):
    """해석된 고객 신호를 바탕으로 선택한 다음 action."""

    actual_action: ActionLabel
    reason: str
    selector_source: str
    selector_steps: list[str] = Field(default_factory=list)


class PolicyInput(StrictModel):
    """policy가 참고할 runtime 필드만 담은 입력."""

    ai_current_intent: str
    ai_utterance: str
    user_utterance: str
    user_tone_hint: UserToneHint = UserToneHint.NEUTRAL
    has_user_speech: bool


class Scenario(StrictModel):
    """사람이 라벨링한 expected_action을 포함한 판단 케이스(Scenario) 행."""

    scenario_id: str
    level: int = Field(ge=1)
    domain: str
    ai_current_intent: str
    ai_utterance: str
    user_utterance: str
    event_type: EventType
    expected_action: ActionLabel
    expected_user_intent: str | None
    user_tone_hint: UserToneHint
    has_user_speech: bool
    notes: str

    @model_validator(mode="after")
    def validate_speech_fields(self) -> "Scenario":
        """사용자 발화가 없을 때 발화 텍스트도 비어 있는지 검증한다."""
        if not self.has_user_speech and self.user_utterance != "":
            raise ValueError(
                "user_utterance must be empty when has_user_speech is false"
            )
        return self


class RunnerInput(StrictModel):
    """명령행, API, UI 재생, 평가기가 공통으로 쓰는 런타임 입력."""

    scenario_id: str | None = None
    domain: str | None = None
    level: int | None = Field(default=None, ge=1)
    ai_current_intent: str
    ai_utterance: str
    user_utterance: str
    event_type: EventType
    expected_user_intent: str | None = None
    user_tone_hint: UserToneHint = UserToneHint.NEUTRAL
    has_user_speech: bool
    notes: str | None = None

    @classmethod
    def from_scenario(cls, scenario: Scenario) -> "RunnerInput":
        """판단 케이스(Scenario)를 정책 실행용 입력으로 변환한다."""
        return cls(
            scenario_id=scenario.scenario_id,
            domain=scenario.domain,
            level=scenario.level,
            ai_current_intent=scenario.ai_current_intent,
            ai_utterance=scenario.ai_utterance,
            user_utterance=scenario.user_utterance,
            event_type=scenario.event_type,
            expected_user_intent=scenario.expected_user_intent,
            user_tone_hint=scenario.user_tone_hint,
            has_user_speech=scenario.has_user_speech,
            notes=scenario.notes,
        )

    def to_policy_input(self) -> PolicyInput:
        """policy 호출에 필요한 runtime 필드만 추려 반환한다."""
        return PolicyInput(
            ai_current_intent=self.ai_current_intent,
            ai_utterance=self.ai_utterance,
            user_utterance=self.user_utterance,
            user_tone_hint=self.user_tone_hint,
            has_user_speech=self.has_user_speech,
        )


class PolicyDecision(StrictModel):
    """예상 행동과 비교하기 전의 정책 단일 판단 결과."""

    policy_name: str
    actual_action: ActionLabel
    reason: str
    signals: dict[str, Any] = Field(default_factory=dict)
    stage_latencies_ms: dict[str, float] = Field(default_factory=dict)
    latency_ms: float = 0.0


class RunDecisionLog(StrictModel):
    """Test Bench run artifact에 저장되는 판단 케이스(Scenario)별 판단 로그."""

    scenario_id: str
    policy_name: str
    event_type: EventType
    expected_action: ActionLabel
    actual_action: ActionLabel
    reason: str
    signals: dict[str, Any] = Field(default_factory=dict)
    stage_latencies_ms: dict[str, float] = Field(default_factory=dict)
    latency_ms: float = 0.0
    primary_failure: PrimaryFailure | None = None
