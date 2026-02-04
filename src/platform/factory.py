from __future__ import annotations

from typing import Any, Dict

from src.platform.base import PlatformClient
from src.platform.dify import DifyClient


def build_platform(platform_name: str, platforms_cfg: Dict[str, Any]) -> PlatformClient:
    name = platform_name.lower()
    if name == "dify":
        cfg = platforms_cfg.get("dify", {})
        return DifyClient(
            base_url=str(cfg.get("base_url", "")),
            api_key=str(cfg.get("api_key", "")),
            user=str(cfg.get("user", "")),
            response_mode=str(cfg.get("response_mode", "blocking")),
            timeout_seconds=int(cfg.get("timeout_seconds", 60)),
            query_field=str(cfg.get("query_field", "query")),
            route=str(cfg.get("route", "chat-messages")),
        )
    raise ValueError(f"Unsupported platform: {platform_name}")
