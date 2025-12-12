from __future__ import annotations

from textwrap import dedent
from typing import Optional

from app.agents.base import LLMJsonAgent
from app.schemas.pipeline import AnalystPlan, ManualBundle, AutotestBundle, OptimizationReport

SYSTEM_PROMPT = """
You are a QA optimization assistant. Return JSON with keys duplicates(list), conflicts(list), gaps(list), suggestions(list) using the provided plan and tests.
"""


class OptimizationAgent(LLMJsonAgent):
    async def optimize(
        self,
        plan: AnalystPlan,
        manual: ManualBundle,
        autotests: AutotestBundle,
        model: Optional[str] = None,
    ) -> OptimizationReport:
        prompt = dedent(
            f"""
            Identify duplicates, conflicts, and gaps across plan, manual tests, and autotests.
            Plan: {plan.json(indent=2)}
            Manual cases: {len(manual.cases)}
            Autotest counts: ui={len(autotests.ui)}, api={len(autotests.api)}
            """
        )
        data = await self.run(prompt, model=model, system=SYSTEM_PROMPT)
        return OptimizationReport.parse_obj(data)
