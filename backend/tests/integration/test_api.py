import sys
from pathlib import Path
import pytest

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from app.main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    async def fake_chat_completion(*args, **kwargs):
        # return minimal valid JSON
        return "{\"features\": [], \"flows\": [], \"entities\": [], \"constraints\": [], \"risks\": [], \"coverage_matrix\": {}, \"gaps\": []}"

    async def fake_models(*args, **kwargs):
        return {"data": [{"id": "ai-sage/GigaChat3-10B-A1.8B"}]}

    from app.llm import client as llm_client

    monkeypatch.setattr(llm_client.CloudRuLLMClient, "chat_completion", fake_chat_completion)
    monkeypatch.setattr(llm_client.CloudRuLLMClient, "list_models", fake_models)
    yield


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_create_run():
    resp = client.post("/api/runs", json={"requirements": "sample"})
    assert resp.status_code == 200
    run_id = resp.json()["run_id"]
    assert run_id
