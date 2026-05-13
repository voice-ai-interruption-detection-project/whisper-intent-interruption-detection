from __future__ import annotations

from interruption_detection.llm import LLMSignalClient
from interruption_detection.policies.llm_action import LLMActionPolicy


POLICY_V2_GUIDANCE = {
    "focus": "backchannel_noise_no_speech_stabilization",
    "target_failure": "false_stop",
    "rules": [
        (
            "If has_user_speech is false or user_utterance is empty/blank, choose "
            "continue and do not infer a new customer request."
        ),
        (
            "Treat short Korean backchannels such as 네, 음, 알겠어요, 맞아요 as "
            "not intent shifts."
        ),
        (
            "For backchannels, choose continue when no response is needed or "
            "brief_ack when a small acknowledgement helps, then continue the "
            "original AI flow."
        ),
        (
            "Do not stop or switch only because an input adapter detected sound; "
            "there must be a meaningful request in the transcript."
        ),
        (
            "Even if the utterance is short, clear requests such as refund, "
            "cancellation, return, payment issue, or human agent request are not "
            "backchannels."
        ),
    ],
}


POLICY_V2_FEW_SHOTS = [
    {
        "input": {
            "ai_current_intent": "shipping_inquiry",
            "ai_utterance": "Your item is in transit and will arrive tomorrow.",
            "user_utterance": "",
            "has_user_speech": False,
            "user_tone_hint": "neutral",
        },
        "predicted_event_type": "no_speech",
        "predicted_user_intent": None,
        "ambiguity": "low",
    },
    {
        "input": {
            "ai_current_intent": "return_policy",
            "ai_utterance": "You can return unopened items within seven days.",
            "user_utterance": "음, 알겠습니다.",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "predicted_event_type": "backchannel",
        "predicted_user_intent": None,
        "ambiguity": "low",
    },
    {
        "input": {
            "ai_current_intent": "shipping_inquiry",
            "ai_utterance": "Your item is in transit and will arrive tomorrow.",
            "user_utterance": "환불요.",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "predicted_event_type": "intent_shift",
        "predicted_user_intent": "refund_request",
        "ambiguity": "low",
    },
]


class PolicyV2(LLMActionPolicy):
    """짧은 맞장구와 비의미 음성에서 false_stop을 줄이는 정책."""

    def __init__(self, llm_client: LLMSignalClient | None = None) -> None:
        super().__init__(
            name="policy_v2",
            description=(
                "Policy v2: stabilize backchannel, noise, and no-speech handling "
                "with additional guidance and tone hints."
            ),
            prompt_version="policy_v2_backchannel_noise_v1",
            include_label_definitions=True,
            include_few_shots=True,
            include_tone_hint=True,
            policy_guidance=POLICY_V2_GUIDANCE,
            extra_few_shots=POLICY_V2_FEW_SHOTS,
            llm_client=llm_client,
        )
