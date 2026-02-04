from __future__ import annotations

import logging
from typing import Any, Dict

import requests

from src.platform.base import PlatformClient


logger = logging.getLogger(__name__)


def _extract_query(input_data: Dict[str, Any], query_field: str) -> str:
    if query_field in input_data:
        val = input_data.get(query_field)
        return val if isinstance(val, str) else str(val)
    if "query" in input_data:
        val = input_data.get("query")
        return val if isinstance(val, str) else str(val)
    if "input" in input_data:
        val = input_data.get("input")
        return val if isinstance(val, str) else str(val)
    if "text" in input_data:
        val = input_data.get("text")
        return val if isinstance(val, str) else str(val)
    # Fallback: use the first string-like value
    for _, val in input_data.items():
        if isinstance(val, str):
            return val
        if val is not None:
            return str(val)
    return ""


def _build_payload(input_data: Dict[str, Any], user: str, response_mode: str, query_field: str) -> Dict[str, Any]:
    query = _extract_query(input_data, query_field)
    inputs = {k: v for k, v in input_data.items() if k not in {query_field, "query", "input", "text"}}
    if not query and inputs:
        # Last-resort fallback: derive query from first input value
        first_val = next(iter(inputs.values()))
        query = first_val if isinstance(first_val, str) else str(first_val)
    payload = {
        "inputs": inputs,
        "query": query,
        "response_mode": response_mode,
        "user": user,
    }
    return payload


def _normalize_base_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        return base
    return f"{base}/v1"


def _call_dify_http(base_url: str, api_key: str, payload: Dict[str, Any], timeout_seconds: int, route: str) -> Dict[str, Any]:
    url = f"{_normalize_base_url(base_url)}/{route.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    try:
        resp.raise_for_status()
    except Exception:
        return {"error": True, "status_code": resp.status_code, "body": resp.text}
    try:
        return resp.json()
    except Exception:
        return {"raw_text": resp.text}


class DifyClient(PlatformClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        user: str,
        response_mode: str,
        timeout_seconds: int,
        query_field: str = "query",
        route: str = "chat-messages",
    ):
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.api_key = api_key
        self.user = user
        self.response_mode = response_mode
        self.timeout_seconds = timeout_seconds
        self.query_field = query_field
        self.route = route

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Calling Dify app via REST.")
        payload = _build_payload(input_data, self.user, self.response_mode, self.query_field)
        print(payload)
        return _call_dify_http(self.base_url, self.api_key, payload, self.timeout_seconds, self.route)
