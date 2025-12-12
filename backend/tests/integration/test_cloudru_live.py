import os
import pytest

pytest.importorskip("openai")

RUN_EXTERNAL = os.getenv("RUN_EXTERNAL_TESTS") == "1"
API_KEY = os.getenv("CLOUDRU_API_KEY")
BASE_URL = os.getenv("CLOUDRU_BASE_URL", "https://foundation-models.api.cloud.ru/v1")
REQUIRED_MODEL = "ai-sage/GigaChat3-10B-A1.8B"

pytestmark = pytest.mark.skipif(
    not RUN_EXTERNAL or not API_KEY, reason="RUN_EXTERNAL_TESTS not enabled or missing CLOUDRU_API_KEY"
)


@pytest.mark.asyncio
async def test_models_live():
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
    data = await client.models.list()
    payload = data.to_dict()
    assert payload.get("object") == "list"
    assert payload.get("data")


@pytest.mark.asyncio
async def test_chat_completion_live():
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
    models = await client.models.list()
    ids = [m.id for m in models.data]
    model_id = REQUIRED_MODEL if REQUIRED_MODEL in ids else ids[0]
    resp = await client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=20,
    )
    assert resp.choices
