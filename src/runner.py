from __future__ import annotations

import argparse
import json
from pathlib import Path

from interruption_detection.evaluation.evaluator import evaluate_dataset
from interruption_detection.runner import run_scenario
from interruption_detection.scenarios import get_scenario_by_id, load_scenarios


def main() -> int:
    parser = argparse.ArgumentParser(description="Run interruption detection policies.")
    parser.add_argument("--policy", default="baseline")
    parser.add_argument("--dataset", default="data/scenarios.json")
    parser.add_argument("--scenario-id")
    parser.add_argument("--write-results", action="store_true")
    args = parser.parse_args()

    dataset = Path(args.dataset)
    if args.write_results:
        result = evaluate_dataset(
            dataset,
            args.policy,
            source="cli",
            command=" ".join(["python", "src/runner.py", *vars_to_args(args)]),
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.scenario_id:
        scenario = get_scenario_by_id(dataset, args.scenario_id)
        decision = run_scenario(scenario, args.policy)
        print(
            json.dumps(decision.model_dump(mode="json"), ensure_ascii=False, indent=2)
        )
        return 0

    decisions = [
        {
            "scenario_id": scenario.scenario_id,
            "decision": run_scenario(scenario, args.policy).model_dump(mode="json"),
        }
        for scenario in load_scenarios(dataset)
    ]
    print(json.dumps(decisions, ensure_ascii=False, indent=2))
    return 0


def vars_to_args(args: argparse.Namespace) -> list[str]:
    output = ["--policy", args.policy, "--dataset", args.dataset]
    if args.scenario_id:
        output.extend(["--scenario-id", args.scenario_id])
    if args.write_results:
        output.append("--write-results")
    return output


if __name__ == "__main__":
    raise SystemExit(main())
