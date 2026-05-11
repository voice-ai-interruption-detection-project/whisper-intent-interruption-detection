from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


def test_root_serves_static_ui() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Whisper Intent Workbench" in response.text
    assert "단일 케이스 확인" in response.text
    assert "선택한 케이스" in response.text
    assert "Test Bench" in response.text
    assert "/static/js/main.js" in response.text


def test_ui_javascript_uses_api_vocabularies() -> None:
    js = Path("src/backend/static/js/main.js").read_text(encoding="utf-8")

    assert "/schema" in js
    assert "/policies" in js
    assert "/runs" in js
    assert "policy_v1" not in js
    assert "baseline" not in js
    assert "pause" not in js
