from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    yaml = None


@dataclass
class RunConfig:
    n_cases: int
    max_iterations: int
    history_y: int
    history_x: int
    stop_on_success: bool
    output_dir: str
    logs_dir: str


@dataclass
class WorkflowConfig:
    config_path: str
    platform: str


@dataclass
class LLMConfig:
    base_url: str
    api_key: str
    default_model: str
    temperature: float
    max_tokens: int
    models: Dict[str, str]
    extra_body: Dict[str, Any]


@dataclass
class DifyConfig:
    base_url: str
    api_key: str
    user: str
    response_mode: str
    timeout_seconds: int


@dataclass
class AppConfig:
    run: RunConfig
    workflow: WorkflowConfig
    llm: LLMConfig
    platforms: Dict[str, Any]


def _load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load YAML configs. Install requirements.txt.")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_config(path: str) -> AppConfig:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    if p.suffix.lower() in {".yaml", ".yml"}:
        raw = _load_yaml(p)
    elif p.suffix.lower() == ".json":
        raw = _load_json(p)
    else:
        raise ValueError("Config file must be .yaml/.yml/.json")

    run = raw.get("run", {})
    workflow = raw.get("workflow", {})
    llm = raw.get("llm", {})
    platforms = raw.get("platforms", {})

    return AppConfig(
        run=RunConfig(
            n_cases=int(run.get("n_cases", 1)),
            max_iterations=int(run.get("max_iterations", 1)),
            history_y=int(run.get("history_y", 3)),
            history_x=int(run.get("history_x", 2)),
            stop_on_success=bool(run.get("stop_on_success", True)),
            output_dir=str(run.get("output_dir", "data/runs")),
            logs_dir=str(run.get("logs_dir", "logs")),
        ),
        workflow=WorkflowConfig(
            config_path=str(workflow.get("config_path", "")),
            platform=str(workflow.get("platform", "dify")),
        ),
        llm=LLMConfig(
            base_url=str(llm.get("base_url", "")),
            api_key=str(llm.get("api_key", "")),
            default_model=str(llm.get("default_model", llm.get("model", ""))),
            temperature=float(llm.get("temperature", 0.2)),
            max_tokens=int(llm.get("max_tokens", 800)),
            models=dict(llm.get("models", {})),
            extra_body=dict(llm.get("extra_body", {})),
        ),
        platforms=platforms,
    )


def load_workflow_config(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Workflow config not found: {path}")
    if p.suffix.lower() in {".yaml", ".yml"}:
        return _load_yaml(p)
    if p.suffix.lower() == ".json":
        return _load_json(p)
    raise ValueError("Workflow config must be .yaml/.yml/.json")


def dump_workflow_config(data: Dict[str, Any], path: str) -> None:
    p = Path(path)
    if p.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required to dump YAML configs. Install requirements.txt.")
        with p.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=False, sort_keys=False)
        return
    if p.suffix.lower() == ".json":
        with p.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=True, indent=2)
        return
    raise ValueError("Output workflow config must be .yaml/.yml/.json")


def dump_text(text: str, path: str) -> None:
    Path(path).write_text(text, encoding="utf-8")


def dump_json(data: Any, path: str) -> None:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
