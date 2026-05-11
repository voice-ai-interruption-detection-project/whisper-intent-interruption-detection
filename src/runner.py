from __future__ import annotations

import argparse
import json
from pathlib import Path

from interruption_detection.audio.adapter import run_audio_item
from interruption_detection.audio.manifest import (
    audio_path_for_item,
    load_audio_manifest,
)
from interruption_detection.audio.stt import build_transcriber
from interruption_detection.evaluation.audio_evaluator import evaluate_audio_manifest
from interruption_detection.evaluation.evaluator import evaluate_dataset
from interruption_detection.runner import run_scenario
from interruption_detection.scenarios import get_scenario_by_id, load_scenarios


def main() -> int:
    """명령행 인자를 해석해 단일/전체 판단 케이스(Scenario) 실행과 결과 저장을 처리한다."""
    parser = argparse.ArgumentParser(
        description="끼어들기/의도 전환 행동 판단 policy를 실행한다."
    )
    parser.add_argument("--policy", default="baseline")
    parser.add_argument("--dataset", default="data/scenarios.json")
    parser.add_argument("--scenario-id")
    parser.add_argument("--write-results", action="store_true")
    parser.add_argument("--audio-manifest")
    parser.add_argument(
        "--audio-transcriber",
        choices=["precomputed", "whisper"],
        default="precomputed",
    )
    parser.add_argument("--whisper-model")
    args = parser.parse_args()

    dataset = Path(args.dataset)
    if args.audio_manifest:
        return run_audio_mode(args, dataset)

    # 명령행은 결과 저장, 단일 판단 케이스(Scenario) 확인, 전체 재생 세 가지 모드를 가진다.
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


def run_audio_mode(args: argparse.Namespace, dataset: Path) -> int:
    """오디오 manifest를 기준으로 단일/전체 Audio File Test 또는 run artifact 생성을 실행한다."""
    manifest_path = Path(args.audio_manifest)
    transcriber = build_transcriber(
        args.audio_transcriber,
        whisper_model=args.whisper_model,
    )
    if args.write_results:
        result = evaluate_audio_manifest(
            dataset,
            manifest_path,
            args.policy,
            transcriber,
            source="cli",
            command=" ".join(["python", "src/runner.py", *vars_to_args(args)]),
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    manifest = load_audio_manifest(manifest_path)
    items = [
        item
        for item in manifest.items
        if args.scenario_id is None or item.scenario_id == args.scenario_id
    ]
    if args.scenario_id and not items:
        raise ValueError(f"scenario not found in audio manifest: {args.scenario_id}")

    decisions = []
    for item in items:
        scenario = get_scenario_by_id(dataset, item.scenario_id)
        decision = run_audio_item(
            scenario=scenario,
            item=item,
            audio_path=audio_path_for_item(item, manifest_path),
            policy_name=args.policy,
            transcriber=transcriber,
        )
        decisions.append(
            {
                "scenario_id": item.scenario_id,
                "decision": decision.model_dump(mode="json"),
            }
        )

    if args.scenario_id and decisions:
        print(json.dumps(decisions[0]["decision"], ensure_ascii=False, indent=2))
    else:
        print(json.dumps(decisions, ensure_ascii=False, indent=2))
    return 0


def vars_to_args(args: argparse.Namespace) -> list[str]:
    """run_meta에 남길 명령행 인자를 문자열 목록으로 복원한다."""
    output = ["--policy", args.policy, "--dataset", args.dataset]
    if args.scenario_id:
        output.extend(["--scenario-id", args.scenario_id])
    if args.audio_manifest:
        output.extend(["--audio-manifest", args.audio_manifest])
        output.extend(["--audio-transcriber", args.audio_transcriber])
        if args.audio_transcriber == "whisper" and args.whisper_model:
            output.extend(["--whisper-model", args.whisper_model])
    if args.write_results:
        output.append("--write-results")
    return output


if __name__ == "__main__":
    raise SystemExit(main())
