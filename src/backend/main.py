from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

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

# 테스트와 로컬 실험은 app.state로 데이터/출력 경로를 바꿀 수 있다.
app = FastAPI(title="Interruption Detection Workbench")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class PolicyRequest(BaseModel):
    """시나리오 재생에서 사용할 정책 이름 요청."""

    policy: str = "baseline"


class PredictRequest(BaseModel):
    """자유 입력 예측 요청에 정책 이름을 덧붙인 모델."""

    policy: str = "baseline"
    scenario_id: str | None = None
    domain: str | None = None
    level: int | None = Field(default=None, ge=1)
    ai_current_intent: str
    ai_utterance: str
    user_utterance: str
    event_type: EventType = EventType.AMBIGUOUS
    expected_user_intent: str | None = None
    user_tone_hint: UserToneHint = UserToneHint.NEUTRAL
    has_user_speech: bool
    notes: str | None = None


class RunRequest(BaseModel):
    """테스트 벤치 실행 생성을 위한 요청 모델."""

    policy: str = "baseline"
    dataset: str | None = None


@app.get("/")
def index() -> FileResponse:
    """정적 Work Bench UI의 HTML 파일을 반환한다."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    """서버가 살아 있는지 확인하는 간단한 상태 엔드포인트."""
    return {"status": "ok"}


@app.get("/schema")
def schema() -> dict[str, list[str]]:
    """프론트엔드가 사용할 열거형 기반 어휘 목록을 반환한다."""
    return {
        "action_labels": [item.value for item in ActionLabel],
        "event_types": [item.value for item in EventType],
        "user_tone_hints": [item.value for item in UserToneHint],
        "primary_failures": [item.value for item in PrimaryFailure],
    }


@app.get("/policies")
def policies() -> dict[str, object]:
    """등록된 정책 목록과 각 정책 스냅샷을 반환한다."""
    return {"policies": list_policies()}


@app.get("/scenarios")
def scenarios(request: Request) -> dict[str, object]:
    """현재 데이터셋의 전체 시나리오 목록을 반환한다."""
    items = _load_scenarios(request)
    return {
        "count": len(items),
        "scenarios": [item.model_dump(mode="json") for item in items],
    }


@app.get("/scenarios/{scenario_id}")
def scenario_detail(scenario_id: str, request: Request) -> dict[str, object]:
    """시나리오 식별자로 상세 정보를 반환한다."""
    scenario = _get_scenario(request, scenario_id)
    return scenario.model_dump(mode="json")


@app.post("/scenarios/{scenario_id}/predict")
def predict_scenario(
    scenario_id: str,
    request: Request,
    body: PolicyRequest | None = None,
) -> dict[str, object]:
    """선택한 시나리오 하나를 지정 정책으로 재생한다."""
    # 엔드포인트는 얇게 유지한다: 기준 입력을 읽고 공통 실행기를 호출한다.
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
    """시나리오 파일 없이 전달된 입력을 바로 정책에 태운다."""
    payload = body.model_dump(exclude={"policy"})
    try:
        decision = run_input(RunnerInput.model_validate(payload), body.policy)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"expected_action": None, "decision": decision.model_dump(mode="json")}


@app.post("/runs")
def create_run(body: RunRequest, request: Request) -> dict[str, object]:
    """데이터셋 전체 평가를 실행하고 새 실행 산출물을 만든다."""
    # 일괄 지표와 파일 생성 책임은 API 계층이 아니라 평가기에 있다.
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
    """최근 실행 산출물 목록을 반환한다."""
    return {"runs": list_run_artifacts(output_root=_output_root(request))}


@app.get("/runs/{run_id}")
def run_detail(run_id: str, request: Request) -> dict[str, object]:
    """특정 실행 산출물의 상세 내용을 반환한다."""
    try:
        return read_run_artifacts(run_id, output_root=_output_root(request))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _dataset_path(request: Request) -> Path:
    """app.state 재정의를 반영한 데이터셋 경로를 반환한다."""
    return Path(getattr(request.app.state, "dataset_path", DATASET_PATH))


def _output_root(request: Request) -> Path:
    """app.state 재정의를 반영한 실행 출력 루트를 반환한다."""
    return Path(getattr(request.app.state, "output_root", OUTPUT_ROOT))


def _load_scenarios(request: Request):
    """현재 요청 컨텍스트의 데이터셋을 읽고 HTTP 오류로 변환한다."""
    try:
        return load_scenarios(_dataset_path(request))
    except ScenarioLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _get_scenario(request: Request, scenario_id: str):
    """시나리오 조회 실패를 HTTP 404로 변환해 반환한다."""
    try:
        return get_scenario_by_id(_dataset_path(request), scenario_id)
    except ScenarioLoadError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
