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


def test_generate_manual_ui():
    resp = client.post("/api/generate/manual/ui", json={"requirements": "sample"})
    assert resp.status_code == 200
    data = resp.json()
    assert "@allure.title" in data["code"]
