import logging
from pathlib import Path


def setup_logging(logs_dir: str, run_id: str) -> str:
    Path(logs_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(logs_dir) / f"run_{run_id}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return str(log_path)
