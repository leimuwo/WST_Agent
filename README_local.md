# Safety Testing Framework for Low-Code Agent Workflows

This project scaffolds a Python framework to synthesize and execute security test cases against low-code agent workflows (default: Dify). It uses OpenAI-compatible LLM calls for summarization, idea generation, input/rule generation, and evaluation.

## Quick Start

1. Create and fill a config file, e.g. `config/example.yaml`.
2. Install deps:
   
   ```bash
   pip install -r requirements.txt
   ```
3. Run:
   
   ```bash
   python run.py --config config/example.yaml
   ```

## Outputs

Each run creates a folder under `data/runs/<run_id>/` with:
- `workflow_cleaned.<ext>`: cleaned workflow config
- `workflow_description.txt`: detailed natural language description
- `executions.jsonl`: all iteration records (up to n x m)
- `final_outputs.jsonl`: final n records
- `config_snapshot.json`: full run config

Logs are saved under `logs/`.

## Notes
- All model calls are OpenAI-compatible via `LLMClient`, and can be configured per-role with `llm.models`.
- Dify integration uses direct REST calls. Configure the route in the config file.
