from __future__ import annotations

import logging
from typing import Any, Dict, List

from openai import OpenAI


logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        default_model: str,
        temperature: float,
        max_tokens: int,
        extra_body: Dict[str, Any] | None = None,
    ):
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.api_key = api_key
        self.default_model = default_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extra_body = extra_body or {}
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url or None)

    def chat(self, messages: List[Dict[str, Any]], *, model: str | None = None, **kwargs: Any) -> str:
        used_model = model or self.default_model
        logger.debug("LLM request model: %s", used_model)
        extra_body = kwargs.get("extra_body", None)
        if extra_body is None:
            extra_body = self.extra_body
        resp = self._client.chat.completions.create(
            model=used_model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            extra_body=extra_body if extra_body else None,
        )
        try:
            return (resp.choices[0].message.content or "").strip()
        except Exception as exc:  # pragma: no cover - guard
            raise RuntimeError(f"Unexpected LLM response: {resp}") from exc
