from __future__ import annotations

from textwrap import dedent
from typing import Optional

from app.agents.base import LLMJsonAgent
from app.schemas.pipeline import AnalystPlan, ManualBundle, AutotestBundle

SYSTEM_PROMPT = """
You are a QA automation engineer. Return JSON with keys 'ui' and 'api', each list of tests {name,steps,assertions,target,negative(bool)}. Use Playwright for UI targets and pytest+httpx for API targets. Include positive and negative cases.
"""


class AutotestsAgent(LLMJsonAgent):
    async def generate(self, plan: AnalystPlan, manual: ManualBundle, model: Optional[str] = None) -> AutotestBundle:
        prompt = dedent(
            f"""
            Build autotest plans using manual cases and plan.
            Plan:\n{plan.json(indent=2)}\nManual cases count: {len(manual.cases)}
            """
        )
        data = await self.run(prompt, model=model, system=SYSTEM_PROMPT)
        for key in ["ui", "api"]:
            if key in data:
                for test in data[key]:
                    test["name"] = str(test.get("name", ""))
                    test["steps"] = [str(s) for s in test.get("steps", [])]
                    test["assertions"] = [str(a) for a in test.get("assertions", [])]
                    test["target"] = str(test.get("target", ""))
        return AutotestBundle.parse_obj(data)
