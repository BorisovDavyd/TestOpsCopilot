import sys
from pathlib import Path
import pytest

pytest.importorskip("openai")
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.llm.client import CloudRuLLMClient
from app.utils.errors import LLMServiceError


@pytest.fixture(autouse=True)
def reset_settings(monkeypatch):
    monkeypatch.setenv("CLOUDRU_API_KEY", "test-key")
    from importlib import reload
    import app.config as app_config

    app_config.get_settings.cache_clear()
    reload(app_config)
    yield
    app_config.get_settings.cache_clear()


@pytest.mark.asyncio
async def test_list_models(monkeypatch):
    class FakeModels:
        def to_dict(self):
            return {"data": [{"id": "model-a"}], "object": "list"}

    class FakeClient:
        async def list(self):
            return FakeModels()

    client = CloudRuLLMClient()
    monkeypatch.setattr(client, "client", type("X", (), {"models": FakeClient()})())
    response = await client.list_models()
    assert response["data"][0]["id"] == "model-a"


@pytest.mark.asyncio
async def test_chat_completion(monkeypatch):
    class FakeChat:
        async def create(self, **kwargs):
            return type("Y", (), {"choices": [type("C", (), {"message": type("M", (), {"content": "hello"})()})()]})()

    client = CloudRuLLMClient()
    monkeypatch.setattr(client, "client", type("X", (), {"chat": type("Z", (), {"completions": FakeChat()})()})())
    result = await client.chat_completion([{"role": "user", "content": "hi"}])
    assert result == "hello"


@pytest.mark.asyncio
async def test_missing_api_key(monkeypatch):
    import app.config as app_config
    monkeypatch.delenv("CLOUDRU_API_KEY", raising=False)
    app_config.get_settings.cache_clear()
    client = CloudRuLLMClient()
    with pytest.raises(LLMServiceError):
        await client.list_models()
