from __future__ import annotations

import json
import wave
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from interruption_detection.evaluation.playground_review import (
    PlaygroundReviewJudgment,
)
from interruption_detection.models import ActionLabel


@pytest.fixture()
def client(tmp_path):
    previous_dataset = getattr(app.state, "dataset_path", None)
    previous_output = getattr(app.state, "output_root", None)
    previous_review_client = getattr(app.state, "playground_review_client", None)
    app.state.dataset_path = Path("data/scenarios.json")
    app.state.output_root = tmp_path
    app.state.playground_review_client = FakePlaygroundReviewClient()
    try:
        yield TestClient(app)
    finally:
        if previous_dataset is None:
            del app.state.dataset_path
        else:
            app.state.dataset_path = previous_dataset
        if previous_output is None:
            del app.state.output_root
        else:
            app.state.output_root = previous_output
        if previous_review_client is None:
            del app.state.playground_review_client
        else:
            app.state.playground_review_client = previous_review_client


class FakePlaygroundReviewClient:
    """테스트에서 실제 LLM 호출 없이 Playground review를 반환한다."""

    def __init__(self) -> None:
        self.requests = []

    def review(self, request):
        self.requests.append(request)

        return PlaygroundReviewJudgment(
            verdict="agree",
            recommended_action=ActionLabel.STOP_AND_SWITCH,
            confidence=0.91,
            reason="The selected action is reasonable for the runtime transcript.",
            reviewer_steps=["read_runtime_context", "compare_policy_action"],
        )

    def snapshot(self) -> dict[str, object]:
        return {
            "provider": "fake",
            "model": "playground-review-fake",
            "response_format": "json_schema",
        }


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_schema_comes_from_enums(client: TestClient) -> None:
    response = client.get("/schema")

    assert response.status_code == 200
    assert response.json()["action_labels"] == [
        "continue",
        "brief_ack",
        "respond_and_continue",
        "stop_and_switch",
        "ask_clarifying",
        "handoff",
    ]


def test_policies_comes_from_registry(client: TestClient) -> None:
    response = client.get("/policies")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()["policies"]] == [
        "baseline",
        "policy_v1",
        "policy_v2",
        "policy_v3",
        "policy_v3_1",
    ]


def test_datasets_comes_from_registry(client: TestClient) -> None:
    response = client.get("/datasets")

    assert response.status_code == 200
    body = response.json()
    assert body["default_dataset_id"] == "core"
    assert [item["id"] for item in body["datasets"]] == [
        "core",
        "policy_v2_edge",
        "policy_v3_edge",
        "policy_v3_challenge",
    ]
    assert body["datasets"][1]["scope"] == "diagnostic"
    assert body["datasets"][1]["input_modes"] == ["text"]
    assert body["datasets"][2]["scope"] == "diagnostic"
    assert body["datasets"][3]["scope"] == "diagnostic"


def test_scenario_predict_uses_runner(client: TestClient) -> None:
    response = client.post(
        "/scenarios/commerce_shipping_follow_001/predict",
        json={"policy": "policy_v1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["expected_actions"] == ["respond_and_continue"]
    assert body["decision"]["actual_action"] == "respond_and_continue"


def test_backchannel_predict_returns_expected_actions(client: TestClient) -> None:
    response = client.post(
        "/scenarios/commerce_backchannel_003/predict",
        json={"policy": "policy_v1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["expected_actions"] == ["continue", "brief_ack"]
    assert body["action_match"] is True


def test_free_predict(client: TestClient) -> None:
    response = client.post(
        "/predict",
        json={
            "policy": "policy_v1",
            "ai_current_intent": "shipping_inquiry",
            "ai_utterance": "Shipping is in progress.",
            "user_utterance": "I want a refund.",
            "event_type": "intent_shift",
            "expected_user_intent": "refund_request",
            "user_tone_hint": "neutral",
            "has_user_speech": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"]["actual_action"] == "stop_and_switch"


def test_playground_review_uses_runtime_input_only(client: TestClient) -> None:
    response = client.post(
        "/playground/reviews",
        json={
            "ai_current_intent": "shipping_inquiry",
            "ai_utterance": "배송 상태를 안내드리겠습니다.",
            "user_utterance": "환불받고 싶어요.",
            "user_tone_hint": "neutral",
            "has_user_speech": True,
            "decision": {
                "policy_name": "policy_v1",
                "actual_action": "stop_and_switch",
                "reason": "The user asks for a refund.",
                "signals": {
                    "predicted_event_type": "intent_shift",
                    "predicted_user_intent": "refund_request",
                },
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["review"]["verdict"] == "agree"
    assert body["review"]["recommended_action"] == "stop_and_switch"
    assert body["review"]["reviewer_snapshot"]["provider"] == "fake"

    request = app.state.playground_review_client.requests[-1]
    assert "expected_actions" not in request.user_prompt
    assert "event_type" not in request.user_prompt
    assert "expected_user_intent" not in request.user_prompt
    assert request.metadata["official_metric"] is False


def test_create_and_read_run(client: TestClient) -> None:
    response = client.post("/runs", json={"policy": "baseline"})

    assert response.status_code == 200
    run_id = response.json()["run_id"]
    assert response.json()["run_meta"]["dataset_id"] == "core"
    assert response.json()["run_meta"]["dataset_scope"] == "official"
    list_response = client.get("/runs")
    assert list_response.status_code == 200
    assert list_response.json()["runs"][0]["run_id"] == run_id
    assert list_response.json()["runs"][0]["dataset_id"] == "core"

    detail = client.get(f"/runs/{run_id}")
    assert detail.status_code == 200
    assert detail.json()["evaluation"]["total"] == 30


def test_create_run_with_policy_v2_edge_dataset(client: TestClient) -> None:
    response = client.post(
        "/runs",
        json={
            "policy": "policy_v2",
            "dataset_id": "policy_v2_edge",
            "input_mode": "text",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["run_meta"]["dataset_id"] == "policy_v2_edge"
    assert body["run_meta"]["dataset_scope"] == "diagnostic"
    assert body["evaluation"]["total"] == 11


def test_create_run_with_policy_v3_edge_dataset(client: TestClient) -> None:
    response = client.post(
        "/runs",
        json={
            "policy": "policy_v2",
            "dataset_id": "policy_v3_edge",
            "input_mode": "text",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["run_meta"]["dataset_id"] == "policy_v3_edge"
    assert body["run_meta"]["dataset_scope"] == "diagnostic"
    assert body["evaluation"]["total"] == 12


def test_create_run_with_policy_v3_challenge_dataset(client: TestClient) -> None:
    response = client.post(
        "/runs",
        json={
            "policy": "policy_v2",
            "dataset_id": "policy_v3_challenge",
            "input_mode": "text",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["run_meta"]["dataset_id"] == "policy_v3_challenge"
    assert body["run_meta"]["dataset_scope"] == "diagnostic"
    assert body["evaluation"]["total"] == 18


def test_create_run_rejects_dataset_input_mode_mismatch(
    client: TestClient,
) -> None:
    response = client.post(
        "/runs",
        json={
            "policy": "policy_v2",
            "dataset_id": "policy_v2_edge",
            "input_mode": "audio_file",
        },
    )

    assert response.status_code == 400
    assert "does not support input_mode" in response.json()["detail"]


def test_create_audio_run(client: TestClient, tmp_path) -> None:
    audio_path = tmp_path / "fixtures" / "refund.wav"
    write_wav(audio_path)
    manifest_path = write_audio_manifest(tmp_path, audio_path)

    response = client.post(
        "/runs",
        json={
            "policy": "policy_v1",
            "input_mode": "audio_file",
            "audio_manifest": str(manifest_path),
            "audio_transcriber": "precomputed",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["evaluation"]["total"] == 1
    assert body["run_meta"]["mode"] == "audio_file"

    list_response = client.get("/runs")
    assert list_response.status_code == 200
    run = list_response.json()["runs"][0]
    assert run["mode"] == "audio_file"
    assert run["target"] == str(manifest_path)
    assert run["input_adapter_snapshot"]["transcriber"]["provider"] == (
        "precomputed_manifest"
    )


def write_audio_manifest(root: Path, audio_path: Path) -> Path:
    manifest_path = root / "audio_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "version": "audio_fixture_v1",
                "items": [
                    {
                        "scenario_id": "commerce_shipping_to_refund_001",
                        "audio_path": str(audio_path.relative_to(root)),
                        "audio_kind": "tts_user_utterance",
                        "transcript_source": "precomputed",
                        "expected_transcript": "아 그게 아니라 환불받고 싶어요.",
                        "expected_has_user_speech": True,
                        "language": "ko",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    return manifest_path


def write_wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 16000
    frames = []

    for index in range(sample_rate // 10):
        value = 1200 if index % 2 == 0 else -1200
        frames.append(value.to_bytes(2, "little", signed=True))

    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(b"".join(frames))
