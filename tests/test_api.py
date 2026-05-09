from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture()
def client(tmp_path):
    previous_dataset = getattr(app.state, "dataset_path", None)
    previous_output = getattr(app.state, "output_root", None)
    app.state.dataset_path = Path("data/scenarios.json")
    app.state.output_root = tmp_path
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
    ]


def test_scenario_predict_uses_runner(client: TestClient) -> None:
    response = client.post(
        "/scenarios/commerce_shipping_follow_001/predict",
        json={"policy": "policy_v1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["expected_action"] == "respond_and_continue"
    assert body["decision"]["actual_action"] == "respond_and_continue"


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


def test_create_and_read_run(client: TestClient) -> None:
    response = client.post("/runs", json={"policy": "baseline"})

    assert response.status_code == 200
    run_id = response.json()["run_id"]
    list_response = client.get("/runs")
    assert list_response.status_code == 200
    assert list_response.json()["runs"][0]["run_id"] == run_id

    detail = client.get(f"/runs/{run_id}")
    assert detail.status_code == 200
    assert detail.json()["evaluation"]["total"] == 30
