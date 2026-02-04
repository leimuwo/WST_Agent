from __future__ import annotations

import json
import re
from typing import Any


_INVALID_ESCAPE_RE = re.compile(r"\\(?![\"\\/bfnrtu])")
_TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")


def extract_json(text: str) -> Any:
    """
    Best-effort JSON extraction/repair for LLM outputs.
    - Removes code fences
    - Extracts the first {...} or [...] block
    - Repairs invalid backslash escapes
    - Removes trailing commas
    """
    cleaned = _strip_code_fences(text).strip()
    # Fast path
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    block = _extract_first_json_block(cleaned)
    if block is None:
        # Re-raise with original text to surface issue upstream
        return json.loads(cleaned)

    for candidate in _repair_candidates(block):
        try:
            return json.loads(candidate)
        except Exception:
            continue

    # Final attempt on the original block to raise a helpful error
    return json.loads(block)


def _strip_code_fences(text: str) -> str:
    # Remove ```json ... ``` or ``` ... ```
    if "```" not in text:
        return text
    return re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", text, flags=re.IGNORECASE)


def _extract_first_json_block(text: str) -> str | None:
    # Try object
    obj_match = re.search(r"\{.*\}", text, re.DOTALL)
    if obj_match:
        return obj_match.group(0)
    # Try array
    arr_match = re.search(r"\[.*\]", text, re.DOTALL)
    if arr_match:
        return arr_match.group(0)
    return None


def _repair_candidates(text: str) -> list[str]:
    candidates = []
    # 1) Fix invalid escapes
    fixed_escapes = _INVALID_ESCAPE_RE.sub(r"\\\\", text)
    candidates.append(fixed_escapes)
    # 2) Remove trailing commas
    candidates.append(_TRAILING_COMMA_RE.sub(r"\1", fixed_escapes))
    # 3) Remove trailing commas without escape fix (alternate path)
    candidates.append(_TRAILING_COMMA_RE.sub(r"\1", text))
    return candidates
