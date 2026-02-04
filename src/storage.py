from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable


def new_run_dir(base_dir: str, run_id: str) -> Path:
    p = Path(base_dir) / run_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_jsonl(path: str, records: Iterable[Dict[str, Any]]) -> None:
    p = Path(path)
    with p.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def append_jsonl(path: str, record: Dict[str, Any]) -> None:
    p = Path(path)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def asdict_safe(obj: Any) -> Dict[str, Any]:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    if isinstance(obj, dict):
        return obj
    return {"value": obj}
