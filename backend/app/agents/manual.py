from __future__ import annotations

from textwrap import dedent
from typing import Optional

from app.agents.base import LLMJsonAgent
from app.schemas.pipeline import AnalystPlan, ManualBundle

SYSTEM_PROMPT = """
You are a senior QA writing Allure TestOps manual tests. Respond ONLY with JSON having key 'cases': list of cases with fields title,severity,owner,priority,feature,story,suite,tags (list),steps (list),expected (list). Follow AAA in steps, at least 10 cases.
"""


class ManualTestsAgent(LLMJsonAgent):
    async def generate(self, plan: AnalystPlan, model: Optional[str] = None) -> ManualBundle:
        prompt = dedent(
            f"""
            Using the analyzed plan below, produce manual test cases.
            Plan JSON:\n{plan.json(indent=2)}
            """
        )
        data = await self.run(prompt, model=model, system=SYSTEM_PROMPT)
        cases = data.get("cases", [])
        for case in cases:
            case["steps"] = [str(s) for s in case.get("steps", [])]
            case["expected"] = [str(e) for e in case.get("expected", [])]
        data["cases"] = cases
        return ManualBundle.parse_obj(data)
