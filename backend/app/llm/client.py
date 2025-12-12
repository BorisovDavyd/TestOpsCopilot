from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from openai import AsyncOpenAI

from app.config import get_settings
from app.utils.logging import configure_logging
from app.utils.errors import LLMServiceError

logger = configure_logging()


class CloudRuLLMClient:
    def __init__(self):
        self.settings = get_settings()
        base_url = self.settings.cloudru_base_url.rstrip("/")
        parsed = urlparse(base_url)
        if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
            logger.warning(
                "Configured CLOUDRU_BASE_URL points to %s; overriding to official external endpoint", base_url
            )
            base_url = "https://foundation-models.api.cloud.ru/v1"
        self.base_url = base_url
        self.client = AsyncOpenAI(api_key=self.settings.cloudru_api_key, base_url=self.base_url)

    def _require_api_key(self):
        if not self.settings.cloudru_api_key:
            raise LLMServiceError(
                detail="CLOUDRU_API_KEY is not set; Cloud.ru foundation models API is external-only and requires a valid token.",
                status_code=401,
            )

    async def list_models(self) -> Dict[str, Any]:
        self._require_api_key()
        try:
            models = await self.client.models.list()
            return models.to_dict()
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to list models: %s", exc)
            raise LLMServiceError(detail=str(exc))

    async def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> str:
        self._require_api_key()
        try:
            completion = await self.client.chat.completions.create(
                model=model or self.settings.model_default,
                messages=messages,
                **kwargs,
            )
            choices = completion.choices
            if not choices:
                raise LLMServiceError(detail="No completion returned")
            return choices[0].message.content or ""
        except Exception as exc:  # noqa: BLE001
            logger.error("Chat completion failed: %s", exc)
            raise LLMServiceError(detail=str(exc))
