from __future__ import annotations

from interruption_detection.llm import LLMActionClient
from interruption_detection.policies.llm_action import LLMActionPolicy


POLICY_V3_GUIDANCE = {
    "focus": "same_intent_question_intent_shift_boundary",
    "target_failure": "false_stop_on_same_intent_question",
    "rules": [
        (
            "First decide whether the user utterance stays inside ai_current_intent "
            "or asks for a different commerce workflow."
        ),
        (
            "Do not choose stop_and_switch only because the user asked a question; "
            "if the question asks details, status, timing, fee, account, method, "
            "or next step inside the current intent, choose respond_and_continue."
        ),
        (
            "Choose stop_and_switch when the utterance asks for a different task "
            "such as refund, cancellation, return pickup, payment retry, shipping "
            "address change, or human agent connection outside the current intent."
        ),
        (
            "Treat similar Korean openings such as 그럼, 아 그럼, 아니면 as weak "
            "signals; route by the requested business task, not by the opening."
        ),
        (
            "Keep no_speech, noise, and short backchannel handling stable: continue "
            "or brief_ack when there is no meaningful request."
        ),
    ],
}


POLICY_V3_FEW_SHOTS = [
    {
        "input": {
            "ai_current_intent": "shipping_inquiry",
            "ai_utterance": "주문하신 상품은 내일 오후에 도착할 예정입니다.",
            "user_utterance": "그럼 배송비는 얼마예요?",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "actual_action": "respond_and_continue",
        "reason": "The user asks a shipping follow-up inside the current intent.",
    },
    {
        "input": {
            "ai_current_intent": "shipping_inquiry",
            "ai_utterance": "주문하신 상품은 내일 오후에 도착할 예정입니다.",
            "user_utterance": "그럼 배송 말고 환불로 바꿔 주세요.",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "actual_action": "stop_and_switch",
        "reason": "The user changes from shipping status to a refund workflow.",
    },
    {
        "input": {
            "ai_current_intent": "payment_issue",
            "ai_utterance": "결제 승인 오류가 있어 결제 수단을 다시 확인해 드리겠습니다.",
            "user_utterance": "이 카드로 다시 결제해도 돼요?",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "actual_action": "respond_and_continue",
        "reason": "The user asks a payment retry question inside the current intent.",
    },
    {
        "input": {
            "ai_current_intent": "payment_issue",
            "ai_utterance": "결제 승인 오류가 있어 결제 수단을 다시 확인해 드리겠습니다.",
            "user_utterance": "결제 말고 배송지는 지금 바꿀 수 있어요?",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "actual_action": "stop_and_switch",
        "reason": "The user moves from payment troubleshooting to shipping address change.",
    },
]


POLICY_V3_1_GUIDANCE = {
    "focus": "return_refund_adjacent_workflow_boundary",
    "target_failure": "missed_switch_between_return_and_refund",
    "rules": [
        *POLICY_V3_GUIDANCE["rules"],
        (
            "Treat return and refund as adjacent but separate workflows when the "
            "current intent is specifically about return pickup, return request, "
            "or return policy."
        ),
        (
            "If ai_current_intent is return_request or return_policy and the "
            "user asks about refund account, refund amount, refund timing, "
            "refund status, deposit timing, or when money will arrive, choose "
            "stop_and_switch."
        ),
        (
            "If ai_current_intent is refund_request and the user asks to schedule, "
            "change, restart, or check return pickup, choose stop_and_switch."
        ),
        (
            "Only choose respond_and_continue inside return_request or return_policy "
            "when the user asks about return eligibility, packaging, pickup address, "
            "pickup date, pickup method, or return application steps."
        ),
    ],
}


POLICY_V3_1_FEW_SHOTS = [
    *POLICY_V3_FEW_SHOTS,
    {
        "input": {
            "ai_current_intent": "return_policy",
            "ai_utterance": "개봉하지 않은 상품은 수령 후 7일 이내 반품할 수 있습니다.",
            "user_utterance": "포장만 뜯었으면 반품 안 돼요?",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "actual_action": "respond_and_continue",
        "reason": "The user asks about return eligibility inside the return-policy workflow.",
    },
    {
        "input": {
            "ai_current_intent": "return_policy",
            "ai_utterance": "개봉하지 않은 상품은 수령 후 7일 이내 반품할 수 있습니다.",
            "user_utterance": "그럼 환불금은 언제 들어와요?",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "actual_action": "stop_and_switch",
        "reason": "Refund timing is a separate refund-status workflow, not a return-policy follow-up.",
    },
    {
        "input": {
            "ai_current_intent": "return_request",
            "ai_utterance": "반품 수거는 접수 후 2~3일 안에 기사님이 방문합니다.",
            "user_utterance": "수거 주소는 어디서 바꿔요?",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "actual_action": "respond_and_continue",
        "reason": "The user asks about return pickup details inside the return-request workflow.",
    },
    {
        "input": {
            "ai_current_intent": "return_request",
            "ai_utterance": "반품 수거는 접수 후 2~3일 안에 기사님이 방문합니다.",
            "user_utterance": "환불 계좌는 어디서 바꿔요?",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "actual_action": "stop_and_switch",
        "reason": "Refund account change is a separate refund workflow, not a return-pickup follow-up.",
    },
    {
        "input": {
            "ai_current_intent": "refund_request",
            "ai_utterance": "환불은 접수 후 영업일 기준 3~5일 안에 처리됩니다.",
            "user_utterance": "환불 전에 반품 수거부터 다시 잡아주세요.",
            "has_user_speech": True,
            "user_tone_hint": "neutral",
        },
        "actual_action": "stop_and_switch",
        "reason": "Return pickup scheduling is a separate return workflow from refund processing.",
    },
]


class PolicyV3(LLMActionPolicy):
    """같은 의도 보충 질문과 업무 전환 경계를 강화하는 prompt-only 정책."""

    def __init__(self, llm_client: LLMActionClient | None = None) -> None:
        super().__init__(
            name="policy_v3",
            description=(
                "Policy v3: distinguish same-intent follow-up questions from "
                "intent shifts with prompt guidance and minimal-pair few-shots."
            ),
            prompt_version="policy_v3_same_intent_boundary_v1",
            include_label_definitions=True,
            include_few_shots=True,
            include_tone_hint=True,
            policy_guidance=POLICY_V3_GUIDANCE,
            extra_few_shots=POLICY_V3_FEW_SHOTS,
            llm_client=llm_client,
        )


class PolicyV31(LLMActionPolicy):
    """반품과 환불 인접 workflow 경계를 명시한 prompt-only 정책."""

    def __init__(self, llm_client: LLMActionClient | None = None) -> None:
        super().__init__(
            name="policy_v3_1",
            description=(
                "Policy v3.1: keep policy_v3 prompt-only structure and strengthen "
                "the return/refund adjacent workflow boundary."
            ),
            prompt_version="policy_v3_1_return_refund_boundary_v1",
            include_label_definitions=True,
            include_few_shots=True,
            include_tone_hint=True,
            policy_guidance=POLICY_V3_1_GUIDANCE,
            extra_few_shots=POLICY_V3_1_FEW_SHOTS,
            llm_client=llm_client,
        )
