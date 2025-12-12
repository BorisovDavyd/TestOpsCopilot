from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from app.llm.client import CloudRuLLMClient
from app.utils.errors import LLMServiceError


class LLMJsonAgent:
    def __init__(self, client: Optional[CloudRuLLMClient] = None):
        self.client = client or CloudRuLLMClient()

    async def run(self, prompt: str, model: Optional[str] = None, system: Optional[str] = None) -> Dict[str, Any]:
        messages: List[Dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        completion = await self.client.chat_completion(
            messages=messages,
            model=model,
            response_format={"type": "json_object"},
        )
        try:
            return json.loads(completion)
        except Exception as exc:  # noqa: BLE001
            raise LLMServiceError(detail=f"Invalid JSON from LLM: {exc}\nRaw: {completion}")
