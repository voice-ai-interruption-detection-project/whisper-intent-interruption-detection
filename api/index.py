from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from backend.main import app  # noqa: E402


# Vercel serverless functions run from a packaged filesystem. Runtime output
# should go under /tmp and repo-local inputs are pinned to absolute paths.
app.state.dataset_path = ROOT_DIR / "data/scenarios.json"
app.state.dataset_registry_path = ROOT_DIR / "data/datasets.json"
app.state.audio_manifest_path = ROOT_DIR / "data/audio/manifest.json"
app.state.output_root = Path("/tmp/whisper-intent-runs")
