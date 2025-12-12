import sys
from pathlib import Path
import pytest

FASTAPI = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_generate_manual_ui_and_history():
    resp = client.post("/api/generate/manual/ui", json={"requirements": "sample"})
    assert resp.status_code == 200
    data = resp.json()
    assert "@allure.title" in data["code"]
    run_id = data["run_id"]

    list_resp = client.get("/api/runs")
    assert list_resp.status_code == 200
    assert any(run["id"] == run_id for run in list_resp.json().get("runs", []))

    details = client.get(f"/api/runs/{run_id}")
    assert details.status_code == 200
    assert "manual_ui.py" in details.json()["files"]
