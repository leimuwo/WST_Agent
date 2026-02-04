from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Tuple

from src.llm.client import LLMClient
from src.llm.json_utils import extract_json
from src.llm import prompts
from src.platform.base import PlatformClient
from src.synthesis.schemas import AttemptRecord, FinalRecord, Label
from src.storage import append_jsonl


logger = logging.getLogger(__name__)


def _extract_json(text: str) -> dict:
    data = extract_json(text)
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object at top level.")
    return data


def _label_from_eval(data: Dict[str, Any]) -> Label:
    return Label(
        execution_success=bool(data.get("execution_success", False)),
        safety_relevance=bool(data.get("safety_relevance", False)),
        rule_input_alignment=bool(data.get("rule_input_alignment", False)),
    )


def _attempt_to_history(attempt: AttemptRecord) -> Dict[str, str]:
    return {
        "idea": attempt.idea,
        "input_data": json.dumps(attempt.input_data, ensure_ascii=True),
        "safety_rules": json.dumps(attempt.safety_rules, ensure_ascii=True),
        "label": json.dumps(attempt.label.__dict__ if attempt.label else {}, ensure_ascii=True),
        "experience_summary": attempt.experience_summary,
    }


def run_synthesis(
    llm: LLMClient,
    platform: PlatformClient,
    cleaned_config_text: str,
    description: str,
    n_cases: int,
    max_iterations: int,
    history_y: int,
    history_x: int,
    stop_on_success: bool,
    executions_path: str,
    llm_models: Dict[str, str] | None = None,
) -> Tuple[List[AttemptRecord], List[FinalRecord]]:
    all_attempts: List[AttemptRecord] = []
    final_records: List[FinalRecord] = []
    final_history: List[AttemptRecord] = []

    for case_id in range(1, n_cases + 1):
        logger.info("Starting case %s", case_id)
        case_attempts: List[AttemptRecord] = []
        experience_summary = ""

        for iteration in range(1, max_iterations + 1):
            if iteration == 1:
                history = [_attempt_to_history(a) for a in final_history[-history_y:]]
                prompt = prompts.prompt_idea_m1(cleaned_config_text, description, history)
                response = llm.chat([
                    {"role": "system", "content": "Output strict JSON only."},
                    {"role": "user", "content": prompt},
                ], model=_pick_model(llm_models, "idea_generation"))
                data = _extract_json(response)
                idea = str(data.get("idea", "")).strip()
                if not idea:
                    raise RuntimeError("LLM returned empty idea.")
            else:
                previous = case_attempts[-1]
                recent = case_attempts[max(0, len(case_attempts) - history_x - 1):-1]
                prompt = prompts.prompt_idea_mgt1(
                    cleaned_config_text,
                    description,
                    {
                        "idea": previous.idea,
                        "input_data": json.dumps(previous.input_data, ensure_ascii=True),
                        "safety_rules": json.dumps(previous.safety_rules, ensure_ascii=True),
                        "experience_summary": previous.experience_summary,
                    },
                    [_attempt_to_history(a) for a in recent],
                )
                response = llm.chat([
                    {"role": "system", "content": "Output strict JSON only."},
                    {"role": "user", "content": prompt},
                ], model=_pick_model(llm_models, "idea_refine"))
                data = _extract_json(response)
                experience_summary = previous.experience_summary
                idea = str(data.get("next_idea", "")).strip()
                if not idea:
                    raise RuntimeError("LLM returned empty next idea.")

            prompt = prompts.prompt_input_rules(idea, experience_summary)
            response = llm.chat([
                {"role": "system", "content": "Output strict JSON only."},
                {"role": "user", "content": prompt},
            ], model=_pick_model(llm_models, "input_rules"))
            data = _extract_json(response)
            input_data = data.get("input_data")
            safety_rules = data.get("safety_rules") or []
            if not isinstance(safety_rules, list):
                raise RuntimeError("safety_rules must be a list.")
            print(input_data)
            execution_result = platform.execute(input_data if isinstance(input_data, dict) else {"input": input_data})

            attempt = AttemptRecord(
                case_id=case_id,
                iteration=iteration,
                idea=idea,
                input_data=input_data,
                safety_rules=safety_rules,
                execution_result=execution_result,
                label=None,
                experience_summary="",
            )
            case_attempts.append(attempt)
            all_attempts.append(attempt)

            eval_data = _evaluate_only(llm, attempt, model=_pick_model(llm_models, "evaluation"))
            attempt.label = _label_from_eval(eval_data)
            attempt.experience_summary = str(eval_data.get("experience_summary", "")).strip()
            append_jsonl(executions_path, _record_to_json(attempt))

            if stop_on_success and _is_success(attempt.label):
                logger.info("Case %s achieved success at iteration %s", case_id, iteration)
                break

        final_attempt = case_attempts[-1]

        final_records.append(
            FinalRecord(
                case_id=case_id,
                idea=final_attempt.idea,
                input_data=final_attempt.input_data,
                safety_rules=final_attempt.safety_rules,
                execution_result=final_attempt.execution_result,
                label=final_attempt.label,
                experience_summary=final_attempt.experience_summary,
            )
        )
        final_history.append(final_attempt)

    return all_attempts, final_records


def _is_success(label: Label | None) -> bool:
    if label is None:
        return False
    return label.execution_success and label.safety_relevance and label.rule_input_alignment


def _evaluate_only(llm: LLMClient, attempt: AttemptRecord, model: str | None = None) -> Dict[str, Any]:
    prompt = prompts.prompt_evaluate_only({
        "idea": attempt.idea,
        "input_data": json.dumps(attempt.input_data, ensure_ascii=True),
        "safety_rules": json.dumps(attempt.safety_rules, ensure_ascii=True),
        "execution_result": json.dumps(attempt.execution_result, ensure_ascii=True),
    })
    response = llm.chat([
        {"role": "system", "content": "Output strict JSON only."},
        {"role": "user", "content": prompt},
    ], model=model)
    return _extract_json(response)


def _record_to_json(attempt: AttemptRecord) -> Dict[str, Any]:
    return {
        "case_id": attempt.case_id,
        "iteration": attempt.iteration,
        "idea": attempt.idea,
        "input_data": attempt.input_data,
        "safety_rules": attempt.safety_rules,
        "execution_result": attempt.execution_result,
        "label": attempt.label.__dict__ if attempt.label else None,
        "experience_summary": attempt.experience_summary,
    }


def _pick_model(llm_models: Dict[str, str] | None, key: str) -> str | None:
    if not llm_models:
        return None
    return llm_models.get(key)
