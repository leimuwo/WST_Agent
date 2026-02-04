from __future__ import annotations

from pathlib import Path


def read_workflow_text(path: str) -> tuple[str, str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Workflow config not found: {path}")
    text = p.read_text(encoding="utf-8")
    ext = p.suffix.lower().lstrip(".")
    return text, ext
