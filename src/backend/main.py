from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from interruption_detection.audio.adapter import run_audio_item
from interruption_detection.audio.manifest import AudioManifestError, AudioManifestItem
from interruption_detection.audio.signals import analyze_audio_file
from interruption_detection.audio.stt import (
    AudioProcessingError,
    build_transcriber,
)
from interruption_detection.evaluation.artifacts import (
    list_run_artifacts,
    read_run_artifacts,
)
from interruption_detection.evaluation.audio_evaluator import evaluate_audio_manifest
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
AUDIO_MANIFEST_PATH = Path("data/audio/manifest.json")
OUTPUT_ROOT = Path("results/runs")
STATIC_DIR = Path(__file__).parent / "static"

# 테스트와 로컬 실험은 app.state로 데이터/출력 경로를 바꿀 수 있다.
app = FastAPI(title="AI 행동 판단 Workbench API")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class PolicyRequest(BaseModel):
    """판단 케이스(Scenario) 재생에서 사용할 정책 이름 요청."""

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
    input_mode: Literal["text", "audio_file"] = "text"
    audio_manifest: str | None = None
    audio_transcriber: Literal["precomputed", "whisper"] = "precomputed"
    whisper_model: str | None = None


@app.get("/")
def index() -> FileResponse:
    """정적 판단 실험 UI의 HTML 파일을 반환한다."""
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
    """현재 데이터셋의 전체 판단 케이스(Scenario) 목록을 반환한다."""
    items = _load_scenarios(request)
    return {
        "count": len(items),
        "scenarios": [item.model_dump(mode="json") for item in items],
    }


@app.get("/scenarios/{scenario_id}")
def scenario_detail(scenario_id: str, request: Request) -> dict[str, object]:
    """판단 케이스(Scenario) 식별자로 상세 정보를 반환한다."""
    scenario = _get_scenario(request, scenario_id)
    return scenario.model_dump(mode="json")


@app.post("/scenarios/{scenario_id}/predict")
def predict_scenario(
    scenario_id: str,
    request: Request,
    body: PolicyRequest | None = None,
) -> dict[str, object]:
    """선택한 판단 케이스(Scenario) 하나를 지정 정책으로 재생한다."""
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
    """판단 케이스(Scenario) 파일 없이 전달된 입력을 바로 정책에 태운다."""
    payload = body.model_dump(exclude={"policy"})
    try:
        decision = run_input(RunnerInput.model_validate(payload), body.policy)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"expected_action": None, "decision": decision.model_dump(mode="json")}


@app.post("/audio/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    transcript: str | None = Form(default=None),
    transcriber: str = Form(default="precomputed"),
    language: str = Form(default="ko"),
) -> dict[str, object]:
    """업로드한 오디오 파일을 transcript adapter로 변환한다."""
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = await _save_upload(file, Path(temp_dir))
        item = _audio_item_from_upload(
            scenario_id="uploaded_audio",
            audio_path=audio_path,
            transcript=transcript,
            transcriber=transcriber,
            language=language,
        )
        try:
            stt = build_transcriber(transcriber)
            result = stt.transcribe(audio_path, item)
        except AudioProcessingError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {
            "transcript": result.model_dump(mode="json"),
            "audio_signal": analyze_audio_file(audio_path).model_dump(mode="json"),
        }


@app.post("/audio/predict")
async def predict_audio(
    request: Request,
    file: UploadFile = File(...),
    scenario_id: str = Form(...),
    policy: str = Form(default="baseline"),
    transcript: str | None = Form(default=None),
    transcriber: str = Form(default="precomputed"),
    language: str = Form(default="ko"),
) -> dict[str, object]:
    """판단 케이스(Scenario) context와 업로드 오디오를 합쳐 같은 runner 경로로 판단한다."""
    scenario = _get_scenario(request, scenario_id)
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = await _save_upload(file, Path(temp_dir))
        item = _audio_item_from_upload(
            scenario_id=scenario_id,
            audio_path=audio_path,
            transcript=transcript,
            transcriber=transcriber,
            language=language,
        )
        try:
            stt = build_transcriber(transcriber)
            decision = run_audio_item(
                scenario=scenario,
                item=item,
                audio_path=audio_path,
                policy_name=policy,
                transcriber=stt,
            )
        except (AudioProcessingError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {
            "scenario_id": scenario.scenario_id,
            "expected_action": scenario.expected_action.value,
            "decision": decision.model_dump(mode="json"),
        }


@app.post("/runs")
def create_run(body: RunRequest, request: Request) -> dict[str, object]:
    """데이터셋 전체 평가를 실행하고 새 실행 산출물을 만든다."""
    # 일괄 지표와 파일 생성 책임은 API 계층이 아니라 평가기에 있다.
    dataset = Path(body.dataset) if body.dataset else _dataset_path(request)
    try:
        if body.input_mode == "audio_file":
            manifest = (
                Path(body.audio_manifest)
                if body.audio_manifest
                else _audio_manifest_path(request)
            )
            result = evaluate_audio_manifest(
                dataset,
                manifest,
                body.policy,
                build_transcriber(
                    body.audio_transcriber,
                    whisper_model=body.whisper_model,
                ),
                output_root=_output_root(request),
                source="api",
                command="POST /runs",
            )
        else:
            result = evaluate_dataset(
                dataset,
                body.policy,
                output_root=_output_root(request),
                source="api",
                command="POST /runs",
            )
    except (
        AudioManifestError,
        AudioProcessingError,
        ScenarioLoadError,
        ValueError,
    ) as exc:
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


def _audio_manifest_path(request: Request) -> Path:
    """app.state 재정의를 반영한 audio manifest 경로를 반환한다."""
    return Path(getattr(request.app.state, "audio_manifest_path", AUDIO_MANIFEST_PATH))


def _load_scenarios(request: Request):
    """현재 요청 컨텍스트의 데이터셋을 읽고 HTTP 오류로 변환한다."""
    try:
        return load_scenarios(_dataset_path(request))
    except ScenarioLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _get_scenario(request: Request, scenario_id: str):
    """판단 케이스(Scenario) 조회 실패를 HTTP 404로 변환해 반환한다."""
    try:
        return get_scenario_by_id(_dataset_path(request), scenario_id)
    except ScenarioLoadError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


async def _save_upload(file: UploadFile, directory: Path) -> Path:
    """FastAPI UploadFile을 임시 경로에 저장하고 빈 파일을 거부한다."""
    suffix = Path(file.filename or "upload.wav").suffix or ".wav"
    path = directory / f"upload{suffix}"
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="audio upload is empty")
    path.write_bytes(content)
    return path


def _audio_item_from_upload(
    *,
    scenario_id: str,
    audio_path: Path,
    transcript: str | None,
    transcriber: str,
    language: str,
) -> AudioManifestItem:
    """업로드 요청 필드를 오디오 adapter 입력 모델로 검증한다."""
    if transcriber not in {"precomputed", "whisper"}:
        raise HTTPException(
            status_code=400,
            detail="unknown transcriber. available: precomputed, whisper",
        )
    normalized_transcript = (
        "" if transcriber == "precomputed" and transcript is None else transcript
    )
    return AudioManifestItem(
        scenario_id=scenario_id,
        audio_path=str(audio_path),
        audio_kind="uploaded_audio",
        transcript_source=transcriber,
        expected_transcript=normalized_transcript,
        expected_has_user_speech=(
            bool(normalized_transcript.strip())
            if normalized_transcript is not None
            else None
        ),
        language=language,
    )
