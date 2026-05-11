from __future__ import annotations

from time import perf_counter

from interruption_detection.models import PolicyDecision, RunnerInput, Scenario
from interruption_detection.policies import get_policy


def run_scenario(scenario: Scenario, policy_name: str) -> PolicyDecision:
    """판단 케이스(Scenario)를 RunnerInput으로 바꿔 지정한 정책을 실행한다."""
    return run_input(RunnerInput.from_scenario(scenario), policy_name)


def run_input(runner_input: RunnerInput, policy_name: str) -> PolicyDecision:
    """공통 입력을 받아 정책을 실행하고 실행기 기준 지연시간을 덧붙인다."""
    # 명령행, API, UI, 평가기가 모두 같은 정책 실행 경로를 통과하게 한다.
    policy = get_policy(policy_name)
    started = perf_counter()
    decision = policy.predict(runner_input)
    policy_ms = (perf_counter() - started) * 1000
    stage_latencies = dict(decision.stage_latencies_ms)
    # 정책 내부 단계가 있으면 유지하고, 실행기가 바깥 실행 시간을 추가한다.
    stage_latencies["policy_ms"] = round(policy_ms, 3)
    return decision.model_copy(
        update={
            "stage_latencies_ms": stage_latencies,
            "latency_ms": round(sum(stage_latencies.values()), 3),
        }
    )
