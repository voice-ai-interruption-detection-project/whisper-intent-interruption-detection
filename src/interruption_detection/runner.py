from __future__ import annotations

from time import perf_counter

from interruption_detection.models import PolicyDecision, RunnerInput, Scenario
from interruption_detection.policies import get_policy


def run_scenario(scenario: Scenario, policy_name: str) -> PolicyDecision:
    return run_input(RunnerInput.from_scenario(scenario), policy_name)


def run_input(runner_input: RunnerInput, policy_name: str) -> PolicyDecision:
    policy = get_policy(policy_name)
    started = perf_counter()
    decision = policy.predict(runner_input)
    policy_ms = (perf_counter() - started) * 1000
    stage_latencies = dict(decision.stage_latencies_ms)
    stage_latencies["policy_ms"] = round(policy_ms, 3)
    return decision.model_copy(
        update={
            "stage_latencies_ms": stage_latencies,
            "latency_ms": round(sum(stage_latencies.values()), 3),
        }
    )
