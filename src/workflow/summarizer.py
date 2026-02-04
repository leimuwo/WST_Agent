from __future__ import annotations

import json
import logging
from typing import Tuple

from src.llm.client import LLMClient
from src.llm.json_utils import extract_json
from src.llm.prompts import prompt_summarize


logger = logging.getLogger(__name__)


def _extract_json(text: str) -> dict:
    data = extract_json(text)
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object at top level.")
    return data


def summarize_workflow(llm: LLMClient, workflow_text: str, ext: str, model: str | None = None) -> Tuple[str, str]:
    prompt = prompt_summarize(workflow_text, ext)
    response = llm.chat([
        {"role": "system", "content": "You are a precise assistant that outputs strict JSON."},
        {"role": "user", "content": prompt},
    ], model=model)
    data = _extract_json(response)
    cleaned = str(data.get("cleaned_config_text", "")).strip()
    description = str(data.get("description", "")).strip()
    if not cleaned or not description:
        raise RuntimeError("LLM summarization returned empty outputs.")
    logger.info("Workflow summarization complete.")
    return cleaned, description
