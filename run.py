from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from src.config import load_config, dump_text, dump_json
from src.llm.client import LLMClient
from src.logging_utils import setup_logging
from src.platform.factory import build_platform
from src.storage import new_run_dir, write_jsonl, asdict_safe
from src.synthesis.runner import run_synthesis
from src.workflow.loader import read_workflow_text
from src.workflow.summarizer import summarize_workflow


logger = logging.getLogger(__name__)


def _build_run_id() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"run_{ts}_{uuid4().hex[:8]}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Safety Testing Framework Runner")
    parser.add_argument("--config", required=True, help="Path to framework config (yaml/json)")
    args = parser.parse_args()

    app_cfg = load_config(args.config)
    run_id = _build_run_id()
    setup_logging(app_cfg.run.logs_dir, run_id)

    run_dir = new_run_dir(app_cfg.run.output_dir, run_id)
    logger.info("Run directory: %s", run_dir)

    workflow_text, ext = read_workflow_text(app_cfg.workflow.config_path)

    llm = LLMClient(
        base_url=app_cfg.llm.base_url,
        api_key=app_cfg.llm.api_key,
        default_model=app_cfg.llm.default_model,
        temperature=app_cfg.llm.temperature,
        max_tokens=app_cfg.llm.max_tokens,
        extra_body=app_cfg.llm.extra_body,
    )

    cleaned_text, description = summarize_workflow(
        llm,
        workflow_text,
        ext,
        model=app_cfg.llm.models.get("summarize") if app_cfg.llm.models else None,
    )

    cleaned_path = run_dir / f"workflow_cleaned.{ext}"
    dump_text(cleaned_text, str(cleaned_path))
    dump_text(description, str(run_dir / "workflow_description.txt"))

    config_snapshot = {
        "run_id": run_id,
        "framework_config": {
            "run": asdict_safe(app_cfg.run),
            "workflow": asdict_safe(app_cfg.workflow),
            "llm": asdict_safe(app_cfg.llm),
            "platforms": app_cfg.platforms,
        },
        "workflow_source_path": app_cfg.workflow.config_path,
    }
    dump_json(config_snapshot, str(run_dir / "config_snapshot.json"))

    platform = build_platform(app_cfg.workflow.platform, app_cfg.platforms)
    executions_path = str(run_dir / "executions.jsonl")

    all_attempts, final_records = run_synthesis(
        llm=llm,
        platform=platform,
        cleaned_config_text=cleaned_text,
        description=description,
        n_cases=app_cfg.run.n_cases,
        max_iterations=app_cfg.run.max_iterations,
        history_y=app_cfg.run.history_y,
        history_x=app_cfg.run.history_x,
        stop_on_success=app_cfg.run.stop_on_success,
        executions_path=executions_path,
        llm_models=app_cfg.llm.models,
    )

    finals_json = [
        {
            "case_id": r.case_id,
            "idea": r.idea,
            "input_data": r.input_data,
            "safety_rules": r.safety_rules,
            "execution_result": r.execution_result,
            "label": r.label.__dict__ if r.label else None,
            "experience_summary": r.experience_summary,
        }
        for r in final_records
    ]
    write_jsonl(str(run_dir / "final_outputs.jsonl"), finals_json)

    logger.info("Completed %s cases. Outputs saved in %s", app_cfg.run.n_cases, run_dir)


if __name__ == "__main__":
    main()
