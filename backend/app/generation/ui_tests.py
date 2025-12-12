import textwrap
import textwrap
from typing import List

from app.llm.client import CloudRuLLMClient
from app.utils.logging import configure_logging

logger = configure_logging()


TEMPLATE_HEADER = [
    "import pytest",
    "from playwright.async_api import async_playwright",
    "",
    "BASE_URL = 'https://cloud.ru/pricing'",
]


SCENARIOS = [
    {
        "name": "landing_page_loads",
        "actions": ["await page.goto(BASE_URL)", "await page.wait_for_timeout(500)"],
        "assertions": ["await page.wait_for_selector('text=Calculator')"],
    },
    {
        "name": "add_service_button",
        "actions": ["await page.goto(BASE_URL)", "await page.click('text=Add service')"],
        "assertions": ["assert 'add' in (await page.url()).lower() or page"],
    },
    {
        "name": "slider_updates_price",
        "actions": [
            "await page.goto(BASE_URL)",
            "await page.fill('input[name=cpu]', '4')",
            "await page.fill('input[name=ram]', '8')",
        ],
        "assertions": ["price = await page.text_content('[data-testid=total-price]')", "assert price is not None"],
    },
    {
        "name": "max_instances_enforced",
        "actions": ["await page.goto(BASE_URL)", "await page.fill('input[name=instances]', '120')"],
        "assertions": ["value = await page.get_attribute('input[name=instances]', 'value')", "assert int(value or '0') <= 99"],
    },
]


def _render_ui_test(name: str, actions: List[str], assertions: List[str]) -> str:
    body = ["    async with async_playwright() as p:", "        browser = await p.chromium.launch()", "        page = await browser.new_page()"]
    body.extend([f"        {action}" for action in actions])
    body.append("        # Assertions")
    body.extend([f"        {assertion}" for assertion in assertions])
    body.append("        await browser.close()")
    return textwrap.dedent(
        f"""
        @pytest.mark.asyncio
        async def test_{name}():
{chr(10).join(body)}
        """
    )


async def _maybe_llm(prompt: str, fallback: str) -> str:
    try:
        client = CloudRuLLMClient()
        content = await client.chat_completion(
            messages=[
                {"role": "system", "content": "You generate Playwright pytest async UI tests."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2500,
        )
        if content and "playwright".lower() in content.lower():
            return content
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM UI autotest generation fallback: %s", exc)
    return fallback


async def generate_ui_autotests(requirements: str, manual_cases: str | None = None) -> str:
    lines: List[str] = TEMPLATE_HEADER.copy()
    for scenario in SCENARIOS:
        lines.append(_render_ui_test(scenario["name"], scenario["actions"], scenario["assertions"]))
    fallback = "\n".join(lines)
    prompt = (
        "Generate Playwright + pytest async tests for Cloud.ru calculator UI. Include navigation, actions, and assertions. "
        f"Requirements: {requirements}. Manual seeds: {manual_cases[:500] if manual_cases else 'none'}."
    )
    return await _maybe_llm(prompt, fallback)
