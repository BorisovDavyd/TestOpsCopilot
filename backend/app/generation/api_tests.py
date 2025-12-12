import json
import textwrap
from typing import Dict, Any, List

from app.llm.client import CloudRuLLMClient
from app.utils.logging import configure_logging

logger = configure_logging()


def parse_openapi_spec(openapi_content: str) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore

        parsed = yaml.safe_load(openapi_content)
        if parsed:
            return parsed
    except Exception:
        pass
    try:
        return json.loads(openapi_content)
    except Exception:
        # minimal fallback parser for key paths
        paths: Dict[str, Any] = {}
        for line in openapi_content.splitlines():
            line = line.strip()
            if line.startswith('/'):
                paths[line.split(':')[0]] = {}
        return {"paths": paths}


def _negative_status(responses: Dict[str, Any]) -> str:
    for code in ("401", "403", "404", "422", "400"):
        if code in responses:
            return code
    return "400"


async def _maybe_llm(prompt: str, fallback: str) -> str:
    try:
        client = CloudRuLLMClient()
        content = await client.chat_completion(
            messages=[
                {"role": "system", "content": "You generate runnable pytest API tests using httpx."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=3000,
        )
        if content and "httpx" in content:
            return content
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM API test generation fallback: %s", exc)
    return fallback


async def generate_api_tests_from_spec(openapi_content: str) -> str:
    spec = parse_openapi_spec(openapi_content)
    paths = spec.get("paths", {}) if isinstance(spec, dict) else {}
    lines: List[str] = [
        "import pytest",
        "import httpx",
        "",
        "BASE_URL = 'http://api.example.com'",
        "API_KEY = 'replace-with-token'",
    ]
    for path, methods in list(paths.items())[:10]:
        if not isinstance(methods, dict):
            methods = {"get": {"responses": {"200": {"description": "ok"}}}}
        for method, cfg in list(methods.items())[:2]:
            responses = cfg.get("responses", {}) if isinstance(cfg, dict) else {}
            status = next((code for code in responses if str(code).startswith("2")), "200")
            negative_status = _negative_status(responses)
            func_name = (
                f"test_{method}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '')}" or "test_endpoint"
            )
            lines.append(
                textwrap.dedent(
                    f"""
                    @pytest.mark.asyncio
                    async def {func_name}_positive():
                        async with httpx.AsyncClient(headers={{'Authorization': f'Bearer {{API_KEY}}'}}) as client:
                            response = await client.request('{method.upper()}', f"{{BASE_URL}}{path}")
                        assert response.status_code == {status}
                        assert response.text is not None

                    @pytest.mark.asyncio
                    async def {func_name}_negative():
                        async with httpx.AsyncClient() as client:
                            response = await client.request('{method.upper()}', f"{{BASE_URL}}{path}")
                        assert response.status_code in [{negative_status}, 401, 403, 404, 422]
                    """
                )
            )
    if len(lines) == 5:
        lines.append(
            textwrap.dedent(
                """
                def test_placeholder():
                    assert True
                """
            )
        )
    fallback = "\n".join(lines)
    prompt = (
        "Generate pytest + httpx async API tests from this OpenAPI snippet. Include positive and negative (401/403/404/422) checks, "
        "status assertions, and key field validations. "
        f"Spec: {json.dumps(spec)[:2000]}"
    )
    return await _maybe_llm(prompt, fallback)
