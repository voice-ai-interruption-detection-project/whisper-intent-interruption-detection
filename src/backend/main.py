from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from interruption_detection.evaluation.artifacts import (
    list_run_artifacts,
    read_run_artifacts,
)
from interruption_detection.evaluation.evaluator import evaluate_dataset
from interruption_detection.models import (
    ActionLabel,
    EventType,
    PrimaryFailure,
    RunnerInput,
    UserToneHint,
)
from interruption_detection.policies import list_policies
from interruption_detection.runner import run_input, run_scenario
from interruption_detection.scenarios import (
    ScenarioLoadError,
    get_scenario_by_id,
    load_scenarios,
)


DATASET_PATH = Path("data/scenarios.json")
OUTPUT_ROOT = Path("results/runs")
STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Interruption Detection Workbench")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class PolicyRequest(BaseModel):
    policy: str = "baseline"


class PredictRequest(RunnerInput):
    policy: str = "baseline"


class RunRequest(BaseModel):
    policy: str = "baseline"
    dataset: str | None = None


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/schema")
def schema() -> dict[str, list[str]]:
    return {
        "action_labels": [item.value for item in ActionLabel],
        "event_types": [item.value for item in EventType],
        "user_tone_hints": [item.value for item in UserToneHint],
        "primary_failures": [item.value for item in PrimaryFailure],
    }


@app.get("/policies")
def policies() -> dict[str, object]:
    return {"policies": list_policies()}


@app.get("/scenarios")
def scenarios(request: Request) -> dict[str, object]:
    items = _load_scenarios(request)
    return {
        "count": len(items),
        "scenarios": [item.model_dump(mode="json") for item in items],
    }


@app.get("/scenarios/{scenario_id}")
def scenario_detail(scenario_id: str, request: Request) -> dict[str, object]:
    scenario = _get_scenario(request, scenario_id)
    return scenario.model_dump(mode="json")


@app.post("/scenarios/{scenario_id}/predict")
def predict_scenario(
    scenario_id: str,
    request: Request,
    body: PolicyRequest | None = None,
) -> dict[str, object]:
    policy_name = body.policy if body else "baseline"
    scenario = _get_scenario(request, scenario_id)
    try:
        decision = run_scenario(scenario, policy_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "scenario_id": scenario.scenario_id,
        "expected_action": scenario.expected_action.value,
        "decision": decision.model_dump(mode="json"),
    }


@app.post("/predict")
def predict(body: PredictRequest) -> dict[str, object]:
    payload = body.model_dump(exclude={"policy"})
    try:
        decision = run_input(RunnerInput.model_validate(payload), body.policy)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"decision": decision.model_dump(mode="json")}


@app.post("/runs")
def create_run(body: RunRequest, request: Request) -> dict[str, object]:
    dataset = Path(body.dataset) if body.dataset else _dataset_path(request)
    try:
        result = evaluate_dataset(
            dataset,
            body.policy,
            output_root=_output_root(request),
            source="api",
            command="POST /runs",
        )
    except (ScenarioLoadError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return result


@app.get("/runs")
def list_runs(request: Request) -> dict[str, object]:
    return {"runs": list_run_artifacts(output_root=_output_root(request))}


@app.get("/runs/{run_id}")
def run_detail(run_id: str, request: Request) -> dict[str, object]:
    try:
        return read_run_artifacts(run_id, output_root=_output_root(request))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _dataset_path(request: Request) -> Path:
    return Path(getattr(request.app.state, "dataset_path", DATASET_PATH))


def _output_root(request: Request) -> Path:
    return Path(getattr(request.app.state, "output_root", OUTPUT_ROOT))


def _load_scenarios(request: Request):
    try:
        return load_scenarios(_dataset_path(request))
    except ScenarioLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _get_scenario(request: Request, scenario_id: str):
    try:
        return get_scenario_by_id(_dataset_path(request), scenario_id)
    except ScenarioLoadError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
