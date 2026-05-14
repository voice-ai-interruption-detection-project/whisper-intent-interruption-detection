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
from interruption_detection.datasets import (
    DatasetRegistryError,
    DatasetSpec,
    find_dataset_by_path,
    get_dataset_by_id,
    load_dataset_registry,
)
from interruption_detection.evaluation.artifacts import (
    list_run_artifacts,
    read_run_artifacts,
)
from interruption_detection.evaluation.audio_evaluator import evaluate_audio_manifest
from interruption_detection.evaluation.evaluator import (
    evaluate_dataset,
    is_action_match,
)
from interruption_detection.evaluation.playground_review import (
    PlaygroundReviewInput,
    review_playground_decision,
)
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
DATASET_REGISTRY_PATH = Path("data/datasets.json")
AUDIO_MANIFEST_PATH = Path("data/audio/manifest.json")
OUTPUT_ROOT = Path("results/runs")
STATIC_DIR = Path(__file__).parent / "static"

# 테스트와 로컬 실험은 app.state로 데이터/출력 경로를 바꿀 수 있다.
app = FastAPI(title="Whisper Intent Workbench API")
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
    """Test Bench 실행 생성을 위한 요청 모델."""

    policy: str = "baseline"
    dataset_id: str | None = None
    dataset: str | None = None
    input_mode: Literal["text", "audio_file"] = "text"
    audio_manifest: str | None = None
    audio_transcriber: Literal["precomputed", "whisper"] = "precomputed"
    whisper_model: str | None = None


@app.get("/")
def index() -> FileResponse:
    """Whisper Intent Workbench HTML 파일을 반환한다."""
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


@app.get("/datasets")
def datasets(request: Request) -> dict[str, object]:
    """Test Bench에서 선택할 수 있는 repo-local dataset 목록을 반환한다."""
    try:
        items = load_dataset_registry(_dataset_registry_path(request))
    except DatasetRegistryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "datasets": [item.model_dump(mode="json") for item in items],
        "default_dataset_id": _default_dataset_id(request, items),
    }


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
        "expected_actions": [action.value for action in scenario.expected_actions],
        "action_match": is_action_match(
            scenario.expected_actions,
            decision.actual_action,
        ),
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

    return {"expected_actions": None, "decision": decision.model_dump(mode="json")}


@app.post("/playground/reviews")
def review_playground(
    body: PlaygroundReviewInput,
    request: Request,
) -> dict[str, object]:
    """Playground 단일 판단 결과를 공식 metric과 분리된 LLM review로 점검한다."""
    try:
        review = review_playground_decision(
            body,
            client=_playground_review_client(request),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"review": review.model_dump(mode="json")}


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
            "expected_actions": [action.value for action in scenario.expected_actions],
            "action_match": is_action_match(
                scenario.expected_actions,
                decision.actual_action,
            ),
            "decision": decision.model_dump(mode="json"),
        }


@app.post("/scenarios/{scenario_id}/mic/predict")
async def predict_scenario_mic(
    scenario_id: str,
    request: Request,
    file: UploadFile = File(...),
    policy: str = Form(default="baseline"),
    transcript: str | None = Form(default=None),
    transcriber: str = Form(default="precomputed"),
    language: str = Form(default="ko"),
) -> dict[str, object]:
    """선택한 Scenario context에서 고객 발화만 mic 녹음 transcript로 대체해 판단한다."""
    scenario = _get_scenario(request, scenario_id)

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = await _save_upload(file, Path(temp_dir))

        item = _audio_item_from_upload(
            scenario_id=scenario_id,
            audio_path=audio_path,
            transcript=transcript,
            transcriber=transcriber,
            language=language,
            audio_kind="mic_recording",
        )

        try:
            stt = build_transcriber(transcriber)
            decision = run_audio_item(
                scenario=scenario,
                item=item,
                audio_path=audio_path,
                policy_name=policy,
                transcriber=stt,
                input_mode="mic_trial",
                input_adapter="mic_recording_adapter",
            )
        except (AudioProcessingError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return {
            "scenario_id": scenario.scenario_id,
            "expected_actions": [action.value for action in scenario.expected_actions],
            "action_match": is_action_match(
                scenario.expected_actions,
                decision.actual_action,
            ),
            "decision": decision.model_dump(mode="json"),
        }


@app.post("/runs")
def create_run(body: RunRequest, request: Request) -> dict[str, object]:
    """데이터셋 전체 평가를 실행하고 새 run artifact를 만든다."""
    # 일괄 지표와 파일 생성 책임은 API 계층이 아니라 평가기에 있다.
    try:
        dataset, dataset_snapshot = _resolve_run_dataset(body, request)

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
                dataset_snapshot=dataset_snapshot,
            )
        else:
            result = evaluate_dataset(
                dataset,
                body.policy,
                output_root=_output_root(request),
                source="api",
                command="POST /runs",
                dataset_snapshot=dataset_snapshot,
            )
    except (
        AudioManifestError,
        AudioProcessingError,
        DatasetRegistryError,
        ScenarioLoadError,
        ValueError,
    ) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return result


@app.get("/runs")
def list_runs(request: Request) -> dict[str, object]:
    """최근 run artifact 목록을 반환한다."""
    return {"runs": list_run_artifacts(output_root=_output_root(request))}


@app.get("/runs/{run_id}")
def run_detail(run_id: str, request: Request) -> dict[str, object]:
    """특정 run artifact의 상세 내용을 반환한다."""
    try:
        return read_run_artifacts(run_id, output_root=_output_root(request))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _dataset_path(request: Request) -> Path:
    """app.state 재정의를 반영한 데이터셋 경로를 반환한다."""
    return Path(getattr(request.app.state, "dataset_path", DATASET_PATH))


def _dataset_registry_path(request: Request) -> Path:
    """app.state 재정의를 반영한 dataset registry 경로를 반환한다."""
    return Path(
        getattr(request.app.state, "dataset_registry_path", DATASET_REGISTRY_PATH)
    )


def _output_root(request: Request) -> Path:
    """app.state 재정의를 반영한 run artifact 출력 루트를 반환한다."""
    return Path(getattr(request.app.state, "output_root", OUTPUT_ROOT))


def _audio_manifest_path(request: Request) -> Path:
    """app.state 재정의를 반영한 audio manifest 경로를 반환한다."""
    return Path(getattr(request.app.state, "audio_manifest_path", AUDIO_MANIFEST_PATH))


def _playground_review_client(request: Request):
    """테스트에서 Playground review client를 교체할 수 있게 app.state를 확인한다."""
    return getattr(request.app.state, "playground_review_client", None)


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


def _default_dataset_id(request: Request, items: list[DatasetSpec]) -> str | None:
    """현재 기본 dataset path에 대응하는 registry id를 반환한다."""
    default_path = _dataset_path(request)

    for item in items:
        if Path(item.path) == default_path:
            return item.id

    return items[0].id if items else None


def _resolve_run_dataset(
    body: RunRequest,
    request: Request,
) -> tuple[Path, dict[str, object]]:
    """RunRequest의 dataset 선택을 실제 path와 run metadata snapshot으로 바꾼다."""
    if body.dataset_id and body.dataset:
        raise DatasetRegistryError("dataset_id and dataset must not be used together")

    if body.dataset_id:
        item = get_dataset_by_id(_dataset_registry_path(request), body.dataset_id)
        _ensure_dataset_supports_mode(item, body.input_mode)
        snapshot = item.model_dump(mode="json")

        return Path(item.path), snapshot

    if body.dataset:
        custom_path = Path(body.dataset)

        return custom_path, {
            "id": "custom",
            "label": str(custom_path),
            "path": str(custom_path),
            "scope": "diagnostic",
            "description": "API request dataset path",
            "input_modes": [body.input_mode],
        }

    dataset_path = _dataset_path(request)

    try:
        item = find_dataset_by_path(_dataset_registry_path(request), dataset_path)
    except DatasetRegistryError:
        item = None

    if item is not None:
        _ensure_dataset_supports_mode(item, body.input_mode)

        return dataset_path, item.model_dump(mode="json")

    return dataset_path, {
        "id": "default",
        "label": str(dataset_path),
        "path": str(dataset_path),
        "scope": "official",
        "description": "Default app dataset path",
        "input_modes": [body.input_mode],
    }


def _ensure_dataset_supports_mode(item: DatasetSpec, input_mode: str) -> None:
    """dataset registry의 input_modes와 요청 input_mode를 맞춘다."""
    if input_mode not in item.input_modes:
        modes = ", ".join(item.input_modes)
        raise DatasetRegistryError(
            f"dataset '{item.id}' does not support input_mode '{input_mode}'. "
            f"available: {modes}"
        )


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
    audio_kind: str = "uploaded_audio",
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
        audio_kind=audio_kind,
        transcript_source=transcriber,
        expected_transcript=normalized_transcript,
        expected_has_user_speech=(
            bool(normalized_transcript.strip())
            if normalized_transcript is not None
            else None
        ),
        language=language,
    )
