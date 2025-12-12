from __future__ import annotations
import json
import textwrap
from typing import List

UI_FEATURE = "Cloud.ru Price Calculator"
API_FEATURE = "Evolution Compute API"


def _render_manual_case(index: int, title: str, story: str, steps: List[str], tags: List[str]) -> str:
    step_lines = "\n".join([f"        with allure.step(\"{step}\"):\n            pass" for step in steps])
    block = f"""
    @allure.manual
    @pytest.mark.manual
    @allure.title("{index}. {title}")
    @allure.link("https://cloud.ru")
    @allure.tag({', '.join([repr(tag) for tag in tags])})
    @allure.label("owner", "qa-team")
    @allure.label("priority", "P1")
    @allure.feature("{UI_FEATURE if 'UI' in story else API_FEATURE}")
    @allure.story("{story}")
    @allure.suite("manual")
    class TestCase{index}:
        def test_case(self):
            # Arrange
{step_lines or '            pass'}
            # Act
            # Assert
    """
    return textwrap.dedent(block)


def generate_ui_manual_cases(requirements: str) -> str:
    scenarios = [
        "Verify landing page shows calculator entry point",
        "Add service button opens configurator",
        "Catalog lists core categories",
        "Search filters products",
        "Popular products section visible",
        "Free Tier badge shown for eligible services",
        "Compute configurator CPU slider updates price",
        "RAM selector enforces min and max",
        "Disk options show tooltips",
        "Region dropdown changes currency",
        "Tariff selection updates perks",
        "Dependent fields adjust when switching tariffs",
        "Max instances limited to 99",
        "Price summary updates on quantity change",
        "Remove service updates total",
        "Compare configurations side by side",
        "Download JSON/PDF exports current config",
        "Share link persists selections",
        "Connect button available for valid config",
        "Mobile view collapses navigation",
    ]
    body = ["import allure", "import pytest", "", "@allure.suite('manual-ui')", "class TestCalculatorManualUI:", "    pass", ""]
    for idx, scenario in enumerate(scenarios[:20], start=1):
        steps = ["Arrange calculator page", "Act on element", "Assert expected result"]
        body.append(_render_manual_case(idx, scenario, "UI Flow", steps, ["CRITICAL"]))
    return "\n".join(body)


def _safe_load(content: str):
    try:
        import yaml  # type: ignore

        return yaml.safe_load(content)
    except Exception:
        try:
            return json.loads(content)
        except Exception:
            return {}


def generate_api_manual_cases(openapi_content: str, focus: List[str] | None = None) -> str:
    spec = _safe_load(openapi_content)
    focus = focus or ["vms", "disks", "flavors"]
    paths = spec.get("paths", {}) if isinstance(spec, dict) else {}
    cases: List[str] = ["import allure", "import pytest", ""]
    idx = 1
    for path, methods in paths.items():
        if not any(f"/{f}" in path for f in focus):
            continue
        for method in methods.keys():
            title = f"{method.upper()} {path} returns expected status"
            steps = ["Prepare auth and payload", f"Call {method} {path}", "Validate status and schema"]
            cases.append(_render_manual_case(idx, title, "API Flow", steps, ["NORMAL"]))
            idx += 1
    while idx <= 15:
        title = f"VMs flow happy path #{idx}"
        steps = ["Create VM", "Verify get VM", "Delete VM"]
        cases.append(_render_manual_case(idx, title, "API Flow", steps, ["CRITICAL"]))
        idx += 1
    return "\n".join(cases)
