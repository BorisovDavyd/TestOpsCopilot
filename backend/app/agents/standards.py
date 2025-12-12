from __future__ import annotations

from textwrap import dedent
from typing import Optional

from app.agents.base import LLMJsonAgent
from app.schemas.pipeline import StandardsReport

SYSTEM_PROMPT = """
You are a QA standards auditor. Return JSON with keys: issues (list of {type,severity,location,message,suggestion}), valid (bool). Focus on AAA, Allure labels, naming, structure.
"""


class StandardsAgent(LLMJsonAgent):
    async def audit(self, manual_code: str, autotest_code: str, model: Optional[str] = None) -> StandardsReport:
        prompt = dedent(
            f"""
            Review the following manual and automation code for standards compliance.
            Manual code:\n{manual_code}\n---\nAutotests:\n{autotest_code}
            """
        )
        data = await self.run(prompt, model=model, system=SYSTEM_PROMPT)
        return StandardsReport.parse_obj(data)
