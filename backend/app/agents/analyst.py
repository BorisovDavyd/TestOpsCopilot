from __future__ import annotations

from textwrap import dedent
from typing import Optional

from app.agents.base import LLMJsonAgent
from app.schemas.pipeline import AnalystPlan

SYSTEM_PROMPT = """
You are Requirements Analyst for testing. Return compact JSON with keys: features (list), flows (list), entities (list), constraints (list), risks (list), coverage_matrix (dict from area->list of cases), gaps (list of missing areas). No prose outside JSON.
"""


class AnalystAgent(LLMJsonAgent):
    async def analyze(self, requirements: str, openapi: Optional[str] = None, model: Optional[str] = None) -> AnalystPlan:
        prompt = dedent(
            f"""
            Analyze requirements and/or OpenAPI to produce structured intent map for testing.
            Requirements:\n{requirements}\n---\nOpenAPI (if any):\n{openapi or ''}
            """
        )
        data = await self.run(prompt, model=model, system=SYSTEM_PROMPT)
        for key in ["features", "flows", "entities", "constraints", "risks", "gaps"]:
            if key in data:
                data[key] = [str(item) for item in data.get(key, [])]
        if "coverage_matrix" in data:
            data["coverage_matrix"] = {str(k): [str(x) for x in v] for k, v in data["coverage_matrix"].items()}
        return AnalystPlan.parse_obj(data)
