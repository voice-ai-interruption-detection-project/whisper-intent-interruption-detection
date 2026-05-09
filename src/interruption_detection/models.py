from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrEnum(str, Enum):
    """String enum with values that serialize cleanly to JSON."""

    def __str__(self) -> str:
        return self.value


class ActionLabel(StrEnum):
    CONTINUE = "continue"
    BRIEF_ACK = "brief_ack"
    RESPOND_AND_CONTINUE = "respond_and_continue"
    STOP_AND_SWITCH = "stop_and_switch"
    ASK_CLARIFYING = "ask_clarifying"
    HANDOFF = "handoff"


class EventType(StrEnum):
    NO_SPEECH = "no_speech"
    NOISE = "noise"
    BACKCHANNEL = "backchannel"
    SAME_INTENT_QUESTION = "same_intent_question"
    INTENT_SHIFT = "intent_shift"
    COMPLAINT = "complaint"
    AMBIGUOUS = "ambiguous"


class UserToneHint(StrEnum):
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    URGENT = "urgent"


class PrimaryFailure(StrEnum):
    FALSE_STOP = "false_stop"
    MISSED_SWITCH = "missed_switch"
    ACTION_CONFUSION = "action_confusion"
    AMBIGUOUS_INTENT = "ambiguous_intent"
    STT_UNCERTAINTY = "STT_uncertainty"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=False)


class Scenario(StrictModel):
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
        if not self.has_user_speech and self.user_utterance != "":
            raise ValueError(
                "user_utterance must be empty when has_user_speech is false"
            )
        return self


class RunnerInput(StrictModel):
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


class PolicyDecision(StrictModel):
    policy_name: str
    actual_action: ActionLabel
    reason: str
    signals: dict[str, Any] = Field(default_factory=dict)
    stage_latencies_ms: dict[str, float] = Field(default_factory=dict)
    latency_ms: float = 0.0


class RunDecisionLog(StrictModel):
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
