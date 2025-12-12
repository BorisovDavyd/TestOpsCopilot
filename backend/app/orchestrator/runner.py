from __future__ import annotations

from typing import Dict

from app.agents.analyst import AnalystAgent
from app.agents.manual import ManualTestsAgent
from app.agents.autotests import AutotestsAgent
from app.agents.standards import StandardsAgent
from app.agents.optimize import OptimizationAgent
from app.schemas.pipeline import (
    AnalystPlan,
    AutotestBundle,
    ManualBundle,
    OptimizationReport,
    RunInput,
    RunRecord,
    StepArtifact,
    StepResult,
    StepStatus,
    StandardsReport,
)
from app.storage import artifacts


def render_manual(bundle: ManualBundle) -> str:
    lines = ["import allure", "import pytest", ""]
    for idx, case in enumerate(bundle.cases, start=1):
        lines.extend(
            [
                f"@allure.manual",
                f"@pytest.mark.manual",
                f"@allure.title(\"{idx}. {case.title}\")",
                f"@allure.tag({', '.join([repr(t) for t in case.tags])})",
                f"@allure.label('owner', '{case.owner}')",
                f"@allure.label('priority', '{case.priority}')",
                f"@allure.feature('{case.feature}')",
                f"@allure.story('{case.story}')",
                f"@allure.suite('{case.suite}')",
                f"class TestCase{idx}:",
                "    def test_case(self):",
                "        # Arrange",
                *("        with allure.step(\"" + step + "\"):\n            pass" for step in case.steps),
                "        # Act",
                "        # Assert",
                *("        assert \"" + exp + "\"" for exp in case.expected),
                "",
            ]
        )
    return "\n".join(lines)


def render_autotests(bundle: AutotestBundle) -> Dict[str, str]:
    ui_lines = ["import pytest", "from playwright.async_api import async_playwright", ""]
    for test in bundle.ui:
        ui_lines.append("@pytest.mark.asyncio")
        ui_lines.append(f"async def test_{test.name.replace('-', '_').replace(' ', '_')}():")
        ui_lines.append("    async with async_playwright() as p:")
        ui_lines.append("        browser = await p.chromium.launch()")
        ui_lines.append("        page = await browser.new_page()")
        for step in test.steps:
            ui_lines.append(f"        # {step}")
        ui_lines.append("        # Assertions")
        for assertion in test.assertions:
            ui_lines.append(f"        assert {repr(assertion)}")
        ui_lines.append("        await browser.close()")
        ui_lines.append("")

    api_lines = ["import pytest", "import httpx", "", "BASE_URL = 'http://api.example.com'", ""]
    for test in bundle.api:
        api_lines.append("@pytest.mark.asyncio")
        api_lines.append(f"async def test_{test.name.replace('-', '_').replace(' ', '_')}():")
        api_lines.append("    async with httpx.AsyncClient() as client:")
        for step in test.steps:
            api_lines.append(f"        # {step}")
        api_lines.append("        response = await client.get(BASE_URL)")
        api_lines.append("        # Assertions")
        for assertion in test.assertions:
            api_lines.append(f"        assert {repr(assertion)}")
        if test.negative:
            api_lines.append("        assert response.status_code >= 400")
        api_lines.append("")

    return {"ui_tests.py": "\n".join(ui_lines), "api_tests.py": "\n".join(api_lines)}


class PipelineRunner:
    def __init__(self):
        self.analyst = AnalystAgent()
        self.manual = ManualTestsAgent()
        self.autotests = AutotestsAgent()
        self.standards = StandardsAgent()
        self.optimize = OptimizationAgent()

    async def run(self, run_id: str, inputs: RunInput) -> RunRecord:
        base = artifacts.create_run_folder(run_id)
        steps = {
            "analyst": StepResult(),
            "manual": StepResult(),
            "autotests": StepResult(),
            "standards": StepResult(),
            "optimize": StepResult(),
        }
        record = RunRecord(
            id=run_id,
            input=inputs,
            steps=steps,
            created_at=artifacts.timestamp(),
            updated_at=artifacts.timestamp(),
        )
        artifacts.write_json(base / "input.json", inputs.dict())

        def persist():
            record.updated_at = artifacts.timestamp()
            artifacts.write_json(base / "run.json", record.dict())

        # Analyst
        steps["analyst"].status = StepStatus.running
        steps["analyst"].started_at = artifacts.timestamp()
        plan: AnalystPlan = await self.analyst.analyze(inputs.requirements or "", inputs.openapi, inputs.model)
        steps["analyst"].data = plan.dict()
        steps["analyst"].status = StepStatus.success
        steps["analyst"].finished_at = artifacts.timestamp()
        artifacts.write_json(base / "analyst.json", plan.dict())
        persist()

        # Manual
        steps["manual"].status = StepStatus.running
        steps["manual"].started_at = artifacts.timestamp()
        manual_bundle: ManualBundle = await self.manual.generate(plan, model=inputs.model)
        manual_code = render_manual(manual_bundle)
        artifacts.write_json(base / "manual.json", manual_bundle.dict())
        artifacts.write_text(base / "manual.py", manual_code)
        steps["manual"].status = StepStatus.success
        steps["manual"].finished_at = artifacts.timestamp()
        steps["manual"].artifacts.append(
            StepArtifact(name="manual.py", path=str((base / "manual.py").resolve()))
        )
        persist()

        # Autotests
        steps["autotests"].status = StepStatus.running
        steps["autotests"].started_at = artifacts.timestamp()
        auto_bundle: AutotestBundle = await self.autotests.generate(plan, manual_bundle, model=inputs.model)
        rendered = render_autotests(auto_bundle)
        artifacts.write_json(base / "autotests.json", auto_bundle.dict())
        for fname, content in rendered.items():
            artifacts.write_text(base / fname, content)
            steps["autotests"].artifacts.append(
                StepArtifact(name=fname, path=str((base / fname).resolve()))
            )
        steps["autotests"].status = StepStatus.success
        steps["autotests"].finished_at = artifacts.timestamp()
        persist()

        # Standards
        steps["standards"].status = StepStatus.running
        steps["standards"].started_at = artifacts.timestamp()
        combined_auto = "\n\n".join(rendered.values())
        standards_report: StandardsReport = await self.standards.audit(manual_code, combined_auto, model=inputs.model)
        artifacts.write_json(base / "standards.json", standards_report.dict())
        steps["standards"].data = standards_report.dict()
        steps["standards"].status = StepStatus.success if standards_report.valid else StepStatus.failed
        steps["standards"].finished_at = artifacts.timestamp()
        persist()

        # Optimize
        steps["optimize"].status = StepStatus.running
        steps["optimize"].started_at = artifacts.timestamp()
        optimization: OptimizationReport = await self.optimize.optimize(plan, manual_bundle, auto_bundle, model=inputs.model)
        artifacts.write_json(base / "optimize.json", optimization.dict())
        steps["optimize"].data = optimization.dict()
        steps["optimize"].status = StepStatus.success
        steps["optimize"].finished_at = artifacts.timestamp()
        persist()
        return record

