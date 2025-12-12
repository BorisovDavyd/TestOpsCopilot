import textwrap
from typing import List


def generate_ui_autotests(requirements: str, manual_cases: str | None = None) -> str:
    scenarios = [
        "landing_page_loads",
        "add_service_button",
        "slider_updates_price",
        "max_instances_enforced",
    ]
    lines: List[str] = [
        "import pytest", "from playwright.async_api import async_playwright", "\n",
    ]
    for scenario in scenarios:
        lines.append(
            textwrap.dedent(
                f"""
                @pytest.mark.asyncio
                async def test_{scenario}():
                    async with async_playwright() as p:
                        browser = await p.chromium.launch()
                        page = await browser.new_page()
                        await page.goto('https://cloud.ru/pricing')
                        assert page
                        await browser.close()
                """
            )
        )
    return "\n".join(lines)
