from __future__ import annotations

import json
import textwrap
from typing import List, Dict, Any

UI_FEATURE = "Cloud.ru Price Calculator"
API_FEATURE = "Evolution Compute API"

MANDATORY_DECORATORS = [
    "allure.manual",
    "pytest.mark.manual",
    "allure.title",
    "allure.tag",
    "allure.label",
    "allure.feature",
    "allure.story",
    "allure.suite",
]


def _aaa_steps(arrange: List[str], act: List[str], assert_steps: List[str]) -> str:
    blocks: List[str] = []
    for prefix, steps in ("Arrange", arrange), ("Act", act), ("Assert", assert_steps):
        blocks.append(f"        # {prefix}")
        for step in steps:
            blocks.append(f"        with allure.step(\"{prefix}: {step}\"):\n            pass")
    return "\n".join(blocks)


def _render_manual_case(
    index: int,
    title: str,
    story: str,
    arrange: List[str],
    act: List[str],
    assert_steps: List[str],
    tags: List[str],
    owner: str = "qa-team",
    priority: str = "P1",
    suite: str = "manual",
) -> str:
    steps_block = _aaa_steps(arrange, act, assert_steps)
    block = f"""
    @allure.manual
    @pytest.mark.manual
    @allure.title("{index}. {title}")
    @allure.link("https://cloud.ru")
    @allure.tag({', '.join([repr(tag) for tag in tags])})
    @allure.label("owner", "{owner}")
    @allure.label("priority", "{priority}")
    @allure.feature("{UI_FEATURE if 'UI' in story else API_FEATURE}")
    @allure.story("{story}")
    @allure.suite("{suite}")
    class TestCase{index}:
        def test_case_{index}(self):
{steps_block}
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
    body = [
        "import allure",
        "import pytest",
        "",
        "@allure.suite('manual-ui')",
        "class TestCalculatorManualUI:",
    ]
    for idx, scenario in enumerate(scenarios[:20], start=1):
        arrange = [
            "Open calculator landing page",
            "Ensure user is authenticated or guest per scenario",
        ]
        act = [
            "Interact with the UI control relevant to the scenario",
            "Capture UI state or price changes",
        ]
        assert_steps = [
            "Validate visual state, totals, and constraints",
            "Check Allure attachments if any (screenshots, logs)",
        ]
        tags = ["CRITICAL" if idx <= 10 else "NORMAL"]
        body.append(
            _render_manual_case(
                idx,
                scenario,
                "UI Flow",
                arrange,
                act,
                assert_steps,
                tags,
                suite="manual-ui",
            )
        )
    return "\n\n".join(body)


def _safe_load(content: str) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore

        return yaml.safe_load(content) or {}
    except Exception:
        try:
            return json.loads(content)
        except Exception:
            return {}


def generate_api_manual_cases(openapi_content: str, focus: List[str] | None = None) -> str:
    spec = _safe_load(openapi_content)
    focus = focus or ["vms", "disks", "flavors"]
    paths = spec.get("paths", {}) if isinstance(spec, dict) else {}
    cases: List[str] = ["import allure", "import pytest", "", "@allure.suite('manual-api')", "class TestComputeManualAPI:"]
    idx = 1
    for path, methods in paths.items():
        if not any(f"/{f}" in path for f in focus):
            continue
        for method, cfg in methods.items():
            responses = cfg.get("responses", {}) if isinstance(cfg, dict) else {}
            success_status = next((code for code in responses if code.startswith("2")), "200")
            title = f"{method.upper()} {path} returns {success_status}"
            arrange = ["Prepare auth headers", "Build request payload per OpenAPI schema"]
            act = [f"Send {method.upper()} {path} with valid data"]
            assert_steps = [f"Expect HTTP {success_status}", "Validate key fields in body"]
            cases.append(
                _render_manual_case(
                    idx,
                    title,
                    "API Flow",
                    arrange,
                    act,
                    assert_steps,
                    tags=["CRITICAL" if success_status.startswith("2") else "NORMAL"],
                    suite="manual-api",
                )
            )
            idx += 1
            negative_title = f"{method.upper()} {path} rejects invalid payload"
            negative_arrange = ["Prepare invalid or missing auth", "Use malformed payload"]
            negative_act = [f"Send {method.upper()} {path} with bad data"]
            negative_assert = ["Expect HTTP 400/401/403/404", "Ensure error body contains message or code"]
            cases.append(
                _render_manual_case(
                    idx,
                    negative_title,
                    "API Flow",
                    negative_arrange,
                    negative_act,
                    negative_assert,
                    tags=["LOW"],
                    suite="manual-api",
                )
            )
            idx += 1
    while idx <= 16:
        title = f"VM lifecycle validation #{idx}"
        cases.append(
            _render_manual_case(
                idx,
                title,
                "API Flow",
                ["Create VM with minimal spec", "Record VM id"],
                ["Retrieve VM details", "Delete VM"],
                ["Expect 2xx for create/get/delete", "Ensure cleanup succeeded"],
                tags=["CRITICAL" if idx % 2 == 0 else "NORMAL"],
                suite="manual-api",
            )
        )
        idx += 1
    return "\n\n".join(cases)
