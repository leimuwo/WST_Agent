from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Label:
    execution_success: bool
    safety_relevance: bool
    rule_input_alignment: bool


@dataclass
class AttemptRecord:
    case_id: int
    iteration: int
    idea: str
    input_data: Any
    safety_rules: List[str]
    execution_result: Any
    label: Label | None
    experience_summary: str


@dataclass
class FinalRecord:
    case_id: int
    idea: str
    input_data: Any
    safety_rules: List[str]
    execution_result: Any
    label: Label | None
    experience_summary: str
