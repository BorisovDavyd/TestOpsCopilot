import sys
from pathlib import Path
import pytest

pytest.importorskip("httpx")
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.llm.client import CloudRuLLMClient


@pytest.mark.asyncio
async def test_list_models(monkeypatch):
    import httpx

    client = CloudRuLLMClient()

    async def fake_request(method, url, json=None):
        return httpx.Response(200, json={"data": [{"id": "model-a"}]})

    monkeypatch.setattr(client, "_request_with_retry", fake_request)
    response = await client.list_models()
    assert response["data"][0]["id"] == "model-a"


@pytest.mark.asyncio
async def test_chat_completion(monkeypatch):
    import httpx

    client = CloudRuLLMClient()

    async def fake_request(method, url, json=None):
        return httpx.Response(200, json={"choices": [{"message": {"content": "hello"}}]})

    monkeypatch.setattr(client, "_request_with_retry", fake_request)
    result = await client.chat_completion([{"role": "user", "content": "hi"}])
    assert result == "hello"
