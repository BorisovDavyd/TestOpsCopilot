import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.orchestrator.runner import PipelineRunner
from app.schemas.pipeline import RunInput
from app.llm import client as llm_client


@pytest.mark.asyncio
async def test_pipeline_runner(monkeypatch, tmp_path):
    responses = [
        '{"features":["feat"],"flows":[],"entities":[],"constraints":[],"risks":[],"coverage_matrix":{},"gaps":[]}',
        '{"cases":[{"title":"case1","severity":"CRITICAL","owner":"qa","priority":"P1","feature":"f","story":"s","suite":"manual","tags":["CRITICAL"],"steps":["Arrange"],"expected":["Assert"]}]}',
        '{"ui":[{"name":"ui1","steps":["go"],"assertions":["ok"],"target":"ui","negative":false}],"api":[{"name":"api1","steps":["call"],"assertions":["status"],"target":"api","negative":true}]}',
        '{"issues":[],"valid":true}',
        '{"duplicates":[],"conflicts":[],"gaps":[],"suggestions":[]}',
    ]

    async def fake_chat_completion(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(llm_client.CloudRuLLMClient, "chat_completion", fake_chat_completion)
    monkeypatch.setenv("DATA_PATH", str(tmp_path))
    import app.config as app_config

    app_config.get_settings.cache_clear()

    runner = PipelineRunner()
    record = await runner.run("test", RunInput(requirements="req"))
    assert record.id == "test"
    assert record.steps["analyst"].status.value == "success"
