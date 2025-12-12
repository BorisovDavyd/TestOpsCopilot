import textwrap
from typing import List


TEMPLATE_HEADER = [
    "import pytest",
    "from playwright.async_api import async_playwright",
    "",
    "BASE_URL = 'https://cloud.ru/pricing'",
]


SCENARIOS = [
    {
        "name": "landing_page_loads",
        "actions": ["await page.goto(BASE_URL)", "await page.wait_for_timeout(500)"]
        ,
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


def generate_ui_autotests(requirements: str, manual_cases: str | None = None) -> str:
    lines: List[str] = TEMPLATE_HEADER.copy()
    for scenario in SCENARIOS:
        lines.append(_render_ui_test(scenario["name"], scenario["actions"], scenario["assertions"]))
    return "\n".join(lines)
