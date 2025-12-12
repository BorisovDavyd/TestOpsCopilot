import asyncio
from typing import Any, Dict, List, Optional
import httpx

from app.config import get_settings
from app.utils.logging import configure_logging
from app.utils.errors import LLMServiceError

logger = configure_logging()


class CloudRuLLMClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.cloudru_base_url.rstrip("/")
        # Cloud.ru foundation models API is external-only; guard against accidentally pointing to localhost.
        from urllib.parse import urlparse

        parsed = urlparse(self.base_url)
        if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
            logger.warning(
                "Configured CLOUDRU_BASE_URL points to %s; overriding to official external endpoint", self.base_url
            )
            self.base_url = "https://foundation-models.api.cloud.ru"
        self.headers = {
            "Authorization": f"Bearer {self.settings.cloudru_api_key}" if self.settings.cloudru_api_key else "",
            "Content-Type": "application/json",
        }

    async def _request_with_retry(self, method: str, url: str, json: Optional[Dict[str, Any]] = None):
        backoff = 1
        for attempt in range(self.settings.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.settings.request_timeout) as client:
                    response = await client.request(method, url, headers=self.headers, json=json)
                    if response.status_code >= 500:
                        raise httpx.HTTPStatusError("Server error", request=response.request, response=response)
                    return response
            except (httpx.HTTPError, httpx.HTTPStatusError) as exc:
                logger.warning("LLM request attempt %s failed: %s", attempt + 1, exc)
                if attempt >= self.settings.retries:
                    raise LLMServiceError(detail="LLM service unavailable")
                await asyncio.sleep(backoff)
                backoff *= 2

    async def list_models(self) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/models"
        response = await self._request_with_retry("GET", url)
        if response.status_code != 200:
            raise LLMServiceError(detail=response.text, status_code=response.status_code)
        return response.json()

    async def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": model or self.settings.model_default,
            "messages": messages,
            **kwargs,
        }
        response = await self._request_with_retry("POST", url, json=payload)
        if response.status_code != 200:
            raise LLMServiceError(detail=response.text, status_code=response.status_code)
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise LLMServiceError(detail="No completion returned")
        return choices[0].get("message", {}).get("content", "")
